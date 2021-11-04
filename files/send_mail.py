#!/usr/bin/python3

import sys
from zimbraweb import Response, ZimbraUser, WebkitAttachment

#just for alpha creds
username = open("/secrets/user").read()
password = open("/secrets/password").read()

user = ZimbraUser("https://studgate.dhbw-mannheim.de")
user.login(username, password)
payload, boundary = user.generate_eml_payload(sys.stdin.read())
user.send_raw_payload(payload, boundary)
