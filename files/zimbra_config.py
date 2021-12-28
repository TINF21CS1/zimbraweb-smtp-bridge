import json
from json.decoder import JSONDecodeError
import os
from typing import Dict
import re
import logging
import sys

#setting up logger
import hostnamefilter
#handler = logging.FileHandler(filename='/var/log/log')
handler = logging.StreamHandler(sys.stdout)
handler.addFilter(hostnamefilter.HostnameFilter())
handler.setFormatter(logging.Formatter('%(asctime)s %(hostname)s python/%(filename)s: %(message)s', datefmt='%b %d %H:%M:%S'))
handlers = [handler]
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(handlers=handlers, level=logging.INFO)

CONF_PATH = "/srv/zimbraweb/mnt/config.json"

DEFAULT_CONIFG = {
        "zimbra_host": "https://studgate.dhbw-mannheim.de",
        "email_domain": "student.dhbw-mannheim.de",
        "smtp_fallback": "disabled",
        "smtp_fallback_relay_host": "172.17.0.2",
    }

def main():
    if not os.path.isfile(CONF_PATH):
        if os.environ.get('ENVCONFIG') == "true":
            logging.info("No config file found, creating from ENV.")
            create_config_env()
        else:
            logging.info("No config file found, creating.")
            create_config()
    while not validate_config():
        if os.isatty(0):
            ans = input("Current configuration seems invalid. Recreate (y/n)?")
        else:
            ans = "y"
        while ans not in ["y", "n"]:
            ans = input("Current configuration seems invalid. Recreate (y/n)?")
        if ans == "n":
            return
        else:
            create_config()
    return

def validate_config() -> bool:
    with open(CONF_PATH, "r") as f:
        try:
            config = json.load(f)
        except JSONDecodeError:
            logging.warning("Corrupt config file. (Invalid JSON)")
            return False
    if not "zimbra_host" in config:
        logging.warning("Missing zimbra_host parameter")
        return False
    host = re.match(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", config["zimbra_host"])
    if not host:
        logging.warning("Malformed zimbra_host. You need to include the protocol (http(s)://)!")

    if not "email_domain" in config:
        logging.warning("Missing email_domain parameter")
        return False
    
    email_domain = re.match(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]", config["email_domain"])
    if not email_domain:
        logging.warning("Malformed email_domain. Only include the part after the @ sign.")
        return False
    return True

def create_config():
    if os.isatty(0):
        for key, default in DEFAULT_CONIFG.items():
            if default is not None:
                DEFAULT_CONIFG[key] = input(f"{key} (default: {default}): ") or default
            else:
                DEFAULT_CONIFG[key] = input(f"{key} (default: {default}): ")
    else:
        logging.info("Not running interactively, assuming default values.")

    with open(CONF_PATH, "w") as f:
        json.dump(DEFAULT_CONIFG, f, indent=4)

def create_config_env():
    for key, default in DEFAULT_CONIFG.items():
        DEFAULT_CONIFG[key] = os.getenv(key, default)
        logging.info(f"Wrote key {key} with value {DEFAULT_CONIFG[key]}")

    with open(CONF_PATH, "w") as f:
        json.dump(DEFAULT_CONIFG, f, indent=4)

def get_config() -> Dict[str, str]:
    if not validate_config():
        logging.warning("Invalid configuration! Falling back to default values.")
        return DEFAULT_CONIFG
    with open(CONF_PATH, "r") as f:
            config = json.load(f)
    return config

if __name__ == "__main__":
    main()