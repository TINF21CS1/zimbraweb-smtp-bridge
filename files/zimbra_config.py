import json
from json.decoder import JSONDecodeError
import os
from typing import Dict
import re
import sys

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
            print("No config file found, creating from ENV.")
            create_config_env()
        else:
            print("No config file found, creating.")
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
            print("Corrupt config file. (Invalid JSON)")
            return False
    if not "zimbra_host" in config:
        print("Missing zimbra_host parameter")
        return False
    host = re.match(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", config["zimbra_host"])
    if not host:
        print("Malformed zimbra_host. You need to include the protocol (http(s)://)!", file=sys.stderr)

    if not "email_domain" in config:
        print("Missing email_domain parameter", file=sys.stderr)
        return False
    
    email_domain = re.match(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]", config["email_domain"])
    if not email_domain:
        print("Malformed email_domain. Only include the part after the @ sign.", file=sys.stderr)
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
        print("not running interactively, assuming default values.")

    with open(CONF_PATH, "w") as f:
        json.dump(DEFAULT_CONIFG, f, indent=4)

    if not os.path.isdir("/srv/zimbraweb/mnt/logs"):
        os.mkdir("/srv/zimbraweb/mnt/logs")
        os.chmod("/srv/zimbraweb/mnt/logs", 0o777)

def create_config_env():
    for key, default in DEFAULT_CONIFG.items():
        DEFAULT_CONIFG[key] = os.getenv(key, default)

    with open(CONF_PATH, "w") as f:
        json.dump(DEFAULT_CONIFG, f, indent=4)

    if not os.path.isdir("/srv/zimbraweb/mnt/logs"):
        os.mkdir("/srv/zimbraweb/mnt/logs")
        os.chmod("/srv/zimbraweb/mnt/logs", 0o777)

def get_config() -> Dict[str, str]:
    if not validate_config():
        print("Invalid configuration! Falling back to default values!", file=sys.stderr)
        return DEFAULT_CONIFG
    with open(CONF_PATH, "r") as f:
            config = json.load(f)
    return config

if __name__ == "__main__":
    main()