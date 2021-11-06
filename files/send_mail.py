#!/usr/bin/python3
import sys
import pickle
import logging

from zimbraweb import ZimbraUser

logging.basicConfig(filename='/srv/zimbraweb/logs/send_mail.log', level=logging.INFO)

ZIMBRA_USERNAME = sys.argv[3]

if ZIMBRA_USERNAME.strip() == "":
    # this is probably a bounced email / internal postfix email..
    # TODO
    logging.error("ZIMBRA_USERNAME is empty, unhandled case. (Bounce-Emails)")
    exit(0)

user = ZimbraUser("https://studgate.dhbw-mannheim.de")
with open(f"/dev/shm/auth_{ZIMBRA_USERNAME}", "rb") as f:
    user.session_data = pickle.load(f)
if not user.authenticated:
    logging.error("User is not authenticated, even though a SASL username exists.")
    exit(1)
logging.info("Successfully authenticated.")
payload, boundary = user.generate_eml_payload(sys.stdin.read())
result = user.send_raw_payload(payload, boundary)
logging.info(f"Payload sent: {result=}")
exit(0 if result.success else 1)
