#!/usr/bin/python3

import sys
import os
from zimbra import Response, ZimbraUser, WebkitAttachment

user = ZimbraUser("https://studgate.dhbw-mannheim.de")
user.login(os.getenv('ZIMBRA_USERNAME'), os.getenv('ZIMBRA_PASSWORD'))
payload, boundary = user.generate_eml_payload(sys.stdin.read())
user.send_raw_payload(payload, boundary)
