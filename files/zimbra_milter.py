# A simple milter.

# Author: Stuart D. Gathman <stuart@bmsi.com>
# Copyright 2001 Business Management Systems, Inc.
# This code is under GPL.  See COPYING for details.

import sys
import os
from io import BytesIO
import tempfile
from time import strftime
import logging

import Milter
from Milter import milter

from zimbraweb import emlparsing
from zimbra_config import get_config

#setting up logger
import hostnamefilter
handler = logging.FileHandler(filename='/var/log/log')
#handler = logging.StreamHandler(sys.stdout)
handler.addFilter(hostnamefilter.HostnameFilter())
handler.setFormatter(logging.Formatter('%(asctime)s %(hostname)s python/%(filename)s: %(message)s', datefmt='%b %d %H:%M:%S'))
handlers = [handler]
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(handlers=handlers, level=logging.INFO)

CONFIG = get_config()

class zimbraMilter(Milter.Milter):
    # https://github.com/sdgathman/pymilter/blob/master/sample.py

    def __init__(self):
        self.tempname = None
        self.mailfrom = None
        self.fp = None
        self.bodysize = 0
        self.id = Milter.uniqueID()
        self.user = None

    # multiple messages can be received on a single connection
    # envfrom (MAIL FROM in the SMTP protocol) seems to mark the start
    # of each message.
    @Milter.symlist('{auth_authen}')
    def envfrom(self, f, *str):
        "start of MAIL transaction"
        self.fp = BytesIO()
        self.tempname = None
        self.mailfrom = f
        self.bodysize = 0
        self.user = self.getsymval('{auth_authen}')
        self.auth_type = self.getsymval('{auth_type}')
        if "@" in self.user:
            logging.warning(f"user {self.user} didn't rtfm.")
            self.setreply("530", "5.7.0", "Your username contains the domain, remove it.")
        if self.user:
            logging.info(f"user {self.user} sent mail from {f}")
        else:
            logging.warning(f"unauthenticated mail from {f}")
            self.setreply("530", "5.7.0", "Authentication required")
            return Milter.REJECT

        return Milter.CONTINUE

    @Milter.decode('bytes')
    def header(self, name, val):
        lname = name.lower()
        # log selected headers
        if lname in ('subject', 'x-mailer'):
            logging.debug('%s: %s' % (name, val))
        if self.fp:
            # add header to buffer
            self.fp.write(b"%s: %s\n" % (name.encode(), val))
        return Milter.CONTINUE

    def eoh(self):
        if not self.fp:
            return Milter.TEMPFAIL  # not seen by envfrom
        self.fp.write(b'\n')
        self.fp.seek(0)
        # copy headers to a temp file for scanning the body
        headers = self.fp.getvalue()
        self.fp.close()
        self.tempname = fname = tempfile.mktemp(".eml")
        self.fp = open(fname, "w+b")
        self.fp.write(headers)  # IOError (e.g. disk full) causes TEMPFAIL
        return Milter.CONTINUE

    def body(self, chunk):		# copy body to temp file
        if self.fp:
            self.fp.write(chunk)  # IOError causes TEMPFAIL in milter
            self.bodysize += len(chunk)
        return Milter.CONTINUE

    def _headerChange(self, msg, name, value):
        if value:  # add header
            self.addheader(name, value)
        else:  # delete all headers with name
            h = msg.getheaders(name)
            cnt = len(h)
            for i in range(cnt, 0, -1):
                self.chgheader(name, i-1, '')

    def eom(self):
        if not self.fp:
            return Milter.REJECT
        self.fp.seek(0)

        raw_eml = self.fp.read().decode("utf8")
        if 'From: "Microsoft Outlook" <' in raw_eml:
            # this is a Microsoft Outlook Test message, we need to allow it.
            return Milter.ACCEPT
        if not emlparsing.is_parsable(raw_eml):
            # this is an html email or similar
            if CONFIG['smtp_fallback'] == "enabled":
                logging.info("Zimbra Unparsable EML, but SMTP relay is enabled")
                return Milter.ACCEPT
            else:
                # Reply doesn't show up, not sure why :(
                logging.error("Unsupported EML.")
                self.setreply("554", "5.7.1",
                            "EML with html not supported! Use text/plain or configure smtp_relay.")
                return Milter.REJECT
        return Milter.ACCEPT

    def close(self):
        if self.tempname:
            os.remove(self.tempname)  # remove in case session aborted
        if self.fp:
            self.fp.close()
        if os.path.isfile(f"/dev/shm/auth_{self.user}"):
            os.chmod(f"/dev/shm/auth_{self.user}", 0o444)
        return Milter.CONTINUE

    def abort(self):
        logging.debug("abort after %d body chars" % self.bodysize)
        return Milter.CONTINUE


def runmilter(name, socketname, timeout=0, rmsock=True):
    # The default flags set include everything
    # milter.set_flags(milter.ADDHDRS)
    milter.set_connect_callback(Milter.connect_callback)
    milter.set_helo_callback(lambda ctx, host: ctx.getpriv().hello(host))
    # For envfrom and envrcpt, we would like to convert ESMTP parms to keyword
    # parms, but then all existing users would have to include **kw to accept
    # arbitrary keywords without crashing.  We do provide envcallback and
    # dictfromlist to make parsing the ESMTP args convenient.
    if sys.version < '3.0.0':
        milter.set_envfrom_callback(lambda ctx, *s: ctx.getpriv().envfrom(*s))
        milter.set_envrcpt_callback(lambda ctx, *s: ctx.getpriv().envrcpt(*s))
        milter.set_header_callback(
            lambda ctx, f, v: ctx.getpriv().header(f, v))
    else:
        milter.set_envfrom_callback(
            lambda ctx, *b: ctx.getpriv().envfrom_bytes(*b))
        milter.set_envrcpt_callback(
            lambda ctx, *b: ctx.getpriv().envrcpt_bytes(*b))
        milter.set_header_callback(
            lambda ctx, f, v: ctx.getpriv().header_bytes(f, v))
    milter.set_eoh_callback(lambda ctx: ctx.getpriv().eoh())
    milter.set_body_callback(lambda ctx, chunk: ctx.getpriv().body(chunk))
    milter.set_eom_callback(lambda ctx: ctx.getpriv().eom())
    milter.set_abort_callback(lambda ctx: ctx.getpriv().abort())
    milter.set_close_callback(Milter.close_callback)

    milter.setconn(socketname)

    if timeout > 0:
        milter.settimeout(timeout)
    # disable negotiate callback if runtime version < (1,0,1)
    ncb = Milter.negotiate_callback
    if milter.getversion() < (1, 0, 1):
        ncb = None
    # The name *must* match the X line in sendmail.cf (supposedly)
    milter.register(name,
                    data=lambda ctx: ctx.getpriv().data(),
                    unknown=lambda ctx, cmd: ctx.getpriv().unknown(cmd),
                    negotiate=ncb
                    )

    # We remove the socket here by default on the assumption that you will be
    # starting this filter before sendmail.  If sendmail is not running and the
    # socket already exists, libmilter will throw a warning.  If sendmail is
    # running, this is still safe if there are no messages currently being
    # processed.  It's safer to shutdown sendmail, kill the filter process,
    # restart the filter, and then restart sendmail.
    milter.opensocket(rmsock)
    start_seq = Milter._seq

    logging.debug("Changing chmod of socket to 777")
    os.chmod(socketname, 0o777)

    try:
        milter.main()
    except milter.error:
        if start_seq == Milter._seq:
            raise  # couldn't start
        # milter has been running for a while, but now it can't start new threads
        raise milter.error("out of thread resources")


if __name__ == "__main__":
    #tempfile.tempdir = "/var/log/milter"
    #socketname = "/var/log/milter/pythonsock"
    socketname = "/var/spool/postfix/milter.sock"
    Milter.factory = zimbraMilter
    Milter.set_flags(Milter.CHGBODY + Milter.CHGHDRS + Milter.ADDHDRS)
    logging.info("Starting the Zimbra Milter")
    runmilter("pythonfilter", socketname, 240)
    logging.info("Shutting down..")
