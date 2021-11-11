#!/usr/bin/python3
import sys
import os
import pickle
import logging
from email.parser import Parser

from zimbraweb import ZimbraUser
from zimbraweb import emlparsing

logging.basicConfig(filename='/srv/zimbraweb/logs/send_mail.log', level=logging.INFO)

ZIMBRA_USERNAME = sys.argv[3]
is_bounce = False

user = ZimbraUser("https://studgate.dhbw-mannheim.de")
raw_eml = sys.stdin.read()
parser = Parser()
parsed = parser.parsestr(raw_eml)

if ZIMBRA_USERNAME.strip() == "":
    RECEIVER = sys.argv[2]
    if not os.path.isfile(f"/dev/shm/auth_{RECEIVER}"):
        logging.error("Trying to send unauthenticated bounce-email to non-authenticated user.")
        exit(0)
    else:
        ZIMBRA_USERNAME = RECEIVER
        if "MAILER-DAEMON@" not in parsed.get("From"):
            logging.error("Trying to send non-bounce email to authenticated user.")
            exit(0)
        is_bounce = True
        del parsed["From"]
        parsed["From"] = f"MAILER DAEMON <{RECEIVER}@student.dhbw-mannheim.de>"
        raw_eml = parsed.as_string()

if  f"<{ZIMBRA_USERNAME}@student.dhbw-mannheim.de>" not in parsed.get("From"):
    logging.error(f"User {ZIMBRA_USERNAME} tried to send email claiming to be {parsed.get('From')}")
    exit(0)

failure_code = 1 if not is_bounce else 0 # don't bounce a bounce email or we'll end up in a loop

with open(f"/dev/shm/auth_{ZIMBRA_USERNAME}", "rb") as f:
    try:
        user.session_data = pickle.load(f)
    except pickle.UnpicklingError as e:
        logging.error("failed to read authentication data: ", e)
        exit(failure_code) 
if not user.authenticated:
    logging.error("User is not authenticated, even though a SASL username exists.")
    exit(failure_code)
logging.info("Successfully authenticated.")
with open("/srv/zimbraweb/logs/email.eml", "w") as f:
    f.write(raw_eml)
payload, boundary = emlparsing.parse_eml(user, raw_eml)
result = user.send_raw_payload(payload, boundary)
logging.info(f"Payload sent: {result=}")
exit(0 if result.success else failure_code)
