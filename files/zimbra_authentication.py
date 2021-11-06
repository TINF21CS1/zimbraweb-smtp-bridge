#!/usr/bin/python3
# this *requires* LF line endings!
import os
import sys

from zimbraweb import ZimbraUser

code = 1
logfile = open("/mount/auth.log", "a")
def log(s: str):
    logfile.write(s + "\n")
    logfile.flush()
log("Authentication script called.")

data = os.read(3, 1024).split(b"\x00")
AUTH_USERNAME = data[0].decode("utf8")
AUTH_PASSWORD = data[1].decode("utf8")

log(f"{AUTH_USERNAME=}, {AUTH_PASSWORD=}")

user = ZimbraUser("https://studgate.dhbw-mannheim.de")
if user.login(AUTH_USERNAME, AUTH_PASSWORD):
    log("success, setting ENV variable")
    os.environ["ZIMBRA_USERNAME"] = AUTH_USERNAME
    os.environ["ZIMBRA_PASSWORD"] = AUTH_PASSWORD
    log(f"now calling {sys.argv[1]=}")
    os.system(sys.argv[1])
    exit(0)
else:
    log("failure")
    exit(1)