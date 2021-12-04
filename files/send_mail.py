#!/usr/bin/python3
import sys
import os
import pickle
import logging
from email.parser import Parser

from zimbraweb import WebkitAttachment, ZimbraUser, emlparsing
from zimbra_config import get_config

#### TEMP
#this function should come from zimbraweb.emlparsing in version 2.1, but is temporarily availible directly for testing

def is_parsable(eml: str) -> bool:
    """Check eml string for parsability
    Args:
        eml (str): The EML string to parse.
    Returns:
        bool if parse_eml() will throw an error.
    """

    try:
        emlparsing.parse_eml(eml)
        return True
    except emlparsing.UnsupportedEMLError:
        return False

####

CONFIG = get_config()

file_handler = logging.FileHandler(
    filename='/srv/zimbraweb/logs/send_mail.log')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(handlers=handlers, level=logging.INFO)

logging.info("send_mail started!")

ZIMBRA_USERNAME = sys.argv[3]

if f"@{CONFIG['email_domain']}" in ZIMBRA_USERNAME:
    ZIMBRA_USERNAME = ZIMBRA_USERNAME.replace(f"@{CONFIG['email_domain']}", "")
    logging.error(f"New username: {ZIMBRA_USERNAME}")
is_bounce = False

raw_eml = sys.stdin.read()
parser = Parser()
parsed = parser.parsestr(raw_eml)


def get_auth_user(zimbra_username):
    user = ZimbraUser(CONFIG['zimbra_host'])
    with open(f"/dev/shm/auth_{zimbra_username}", "rb") as f:
        try:
            user.session_data = pickle.load(f)
        except pickle.UnpicklingError as e:
            logging.error("failed to read authentication data: ", e)
            exit(failure_code)
    if not user.authenticated:
        logging.error(
            "User is not authenticated, even though a SASL username exists.")
        exit(failure_code)
    logging.info("Successfully authenticated.")
    return user


def send_as_user(user, payload, boundary):
    result = user.send_raw_payload(payload, boundary)
    logging.info(f"Payload sent: {result=}")
    return result


# this is a bounce email
if ZIMBRA_USERNAME.strip() == "":
    RECEIVER = sys.argv[2]
    if not os.path.isfile(f"/dev/shm/auth_{RECEIVER}"):
        logging.error(
            "Trying to send unauthenticated bounce-email to non-authenticated user.")
        exit(0)
    else:
        ZIMBRA_USERNAME = RECEIVER
        if "MAILER-DAEMON@" not in parsed.get("From"):
            logging.error(
                "Trying to send non-bounce email to authenticated user.")
            exit(0)
        user = get_auth_user(ZIMBRA_USERNAME)
        payload, boundary = user.generate_webkit_payload(to=f"{RECEIVER}@{CONFIG['email_domain']}", subject="Undelivered Mail returned to sender.",
                                                         body="A message you sent could not be delivered. Please see the attached message for the full report.",
                                                         attachments=[WebkitAttachment(filename="bounce.eml", mimetype="application/octet-stream", content=raw_eml.encode("utf8"))])
        result = send_as_user(user, payload, boundary)
        logging.info(f"Bounce sent: {result=}")
        exit(0)

# special case: Outlook test email.
elif parsed["From"] == f'"Microsoft Outlook" <{ZIMBRA_USERNAME}@{CONFIG["email_domain"]}>':
    logging.info("Sending outlook test email via text/plain")
    user = get_auth_user(ZIMBRA_USERNAME)
    result = user.send_mail(to=parsed["To"], subject=parsed["Subject"],
                            body="Diese E-Mail-Nachricht wurde von Microsoft Outlook automatisch während des Testens der Kontoeinstellungen gesendet.")
    logging.info(f"Outlook test email sent: {result=}")
    exit(0 if result.success else 1)

# html mail via local null instance
# TODO: only if config for fallback is set to true
elif not is_parsable(raw_eml):
    logging.info("Mail is unparsable. Using Relay.")
    os.system(f'echo {raw_eml} | sendmail -f "{parsed["From"]}" {parsed["To"]}')

# default: send mail via Zimbra
else:
    if f"{ZIMBRA_USERNAME}@{CONFIG['email_domain']}" not in parsed.get("From"):
        logging.error(
            f"User {ZIMBRA_USERNAME} tried to send email claiming to be {parsed.get('From')}")
        exit(0)

    # don't bounce a bounce email or we'll end up in a loop
    failure_code = 1 if not is_bounce else 0
    user = get_auth_user(ZIMBRA_USERNAME)
    result = user.send_eml(raw_eml)
    logging.info(f"Sent mail, {result=}")
    exit(0 if result.success else failure_code)
