#!/usr/bin/python3

import sys
import zimbraweb

"""
username, password, mailraw, boundary
"""

user = ZimbraUser("https://studgate.dhbw-mannheim.de")
user.login(sys.argv[0], sys.argv[1])
user.send_raw_payload(sys.argv[2], sys.argv[3])