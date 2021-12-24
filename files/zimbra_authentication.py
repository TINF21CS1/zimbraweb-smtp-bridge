#!/usr/bin/python3
# this *requires* LF line endings!
import os
import sys
import pickle
import logging
import sys

from zimbraweb import ZimbraUser
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

data = os.read(3, 1024).split(b"\x00")
AUTH_USERNAME = data[0].decode("utf8")

if f"@{CONFIG['email_domain']}" in AUTH_USERNAME:
    AUTH_USERNAME = AUTH_USERNAME.replace(f"@{CONFIG['email_domain']}", "")

AUTH_PASSWORD = data[1].decode("utf8")

logging.info(f"Trying to authenticate user {AUTH_USERNAME=}")

user = ZimbraUser(CONFIG['zimbra_host'])
if user.login(AUTH_USERNAME, AUTH_PASSWORD):
    logging.info(f"successfully authenticated {AUTH_USERNAME=}")
    with open(f"/dev/shm/auth_{AUTH_USERNAME}", "wb") as f:
        pickle.dump(user.session_data, f, pickle.HIGHEST_PROTOCOL)
    os.chmod(f"/dev/shm/auth_{AUTH_USERNAME}", 0o777)
    os.system(sys.argv[1])
    exit(0)
else:
    logging.warning(f"failed to authenticate {AUTH_USERNAME=}")
    exit(1)
