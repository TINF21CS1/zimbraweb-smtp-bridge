#!/bin/sh
python3 /srv/zimbraweb/zimbra_config.py
/tls.sh
dovecot
postfix start
python3 /srv/zimbraweb/zimbra_milter.py