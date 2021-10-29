#!/usr/bin/python3

import sys
import zimbraweb

user = ZimbraUser("https://studgate.dhbw-mannheim.de")
#user.set_authtoken(sys.argv[0]) #get token from SASL, not yet implemented
user.send_raw_payload(user.generate_eml_payload(sys.stdin.read()))