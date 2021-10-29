#!/usr/bin/python3

import sys
from zimbra import Response, ZimbraUser, WebkitAttachment

user = ZimbraUser("https://studgate.dhbw-mannheim.de")
user.login("s212689", "##")
payload, boundary = user.generate_eml_payload(sys.stdin.read())
user.send_raw_payload(payload, boundary)
