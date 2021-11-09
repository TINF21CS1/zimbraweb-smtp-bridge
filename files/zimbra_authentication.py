#!/usr/bin/python3
# this *requires* LF line endings!
import os
import sys
import pickle
import logging

from zimbraweb import ZimbraUser

logging.basicConfig(filename='/srv/zimbraweb/logs/authentication.log', level=logging.INFO)

data = os.read(3, 1024).split(b"\x00")
AUTH_USERNAME = data[0].decode("utf8")
AUTH_PASSWORD = data[1].decode("utf8")

logging.info(f"Trying to authenticate user {AUTH_USERNAME=}")

user = ZimbraUser("https://studgate.dhbw-mannheim.de")
if user.login(AUTH_USERNAME, AUTH_PASSWORD):
    logging.info(f"successfully authenticated {AUTH_USERNAME=}")
    with open(f"/dev/shm/auth_{AUTH_USERNAME}", "wb") as f:
        pickle.dump(user.session_data, f, pickle.HIGHEST_PROTOCOL)
    os.chmod(f"/dev/shm/auth_{AUTH_USERNAME}", 0o777)
    os.system(sys.argv[1])
    exit(0)
else:
    logging.warning(f"failed to authenticate {AUTH_USERNAME=}")
    exit(1)
