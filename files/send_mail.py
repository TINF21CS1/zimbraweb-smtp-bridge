#!/usr/bin/python3
import sys
import os
import pickle
import logging
from email.parser import Parser

from zimbraweb import WebkitAttachment, ZimbraUser
from zimbraweb import emlparsing

logging.basicConfig(
    filename='/srv/zimbraweb/logs/send_mail.log', level=logging.INFO)

ZIMBRA_USERNAME = sys.argv[3]
is_bounce = False

raw_eml = sys.stdin.read()
parser = Parser()
parsed = parser.parsestr(raw_eml)


def get_auth_user(zimbra_username):
    user = ZimbraUser("https://studgate.dhbw-mannheim.de")
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


if ZIMBRA_USERNAME.strip() == "":  # this is a bounce email
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
        payload, boundary = user.generate_webkit_payload(to=f"{RECEIVER}@student.dhbw-mannheim.de", subject="Undelivered Mail returned to sender.",
                                                         body="A message you sent could not be delivered. Please see the attached message for the full report.",
                                                         attachments=[WebkitAttachment(filename="bounce.eml", mimetype="application/octet-stream", content=raw_eml.encode("utf8"))])
        result = send_as_user(user, payload, boundary)
        logging.info(f"Bounce sent: {result=}")
        exit(0)
else:
    if f"<{ZIMBRA_USERNAME}@student.dhbw-mannheim.de>" not in parsed.get("From"):
        logging.error(
            f"User {ZIMBRA_USERNAME} tried to send email claiming to be {parsed.get('From')}")
        exit(0)

    # don't bounce a bounce email or we'll end up in a loop
    failure_code = 1 if not is_bounce else 0
    user = get_auth_user(ZIMBRA_USERNAME)
    payload, boundary = emlparsing.parse_eml(user, raw_eml)
    result = send_as_user(user, payload, boundary)
    exit(0 if result.success else failure_code)
