#!/bin/sh
python3 /srv/zimbraweb/zimbra_config.py
dovecot
postfix start
python3 /srv/zimbraweb/zimbra_milter.py