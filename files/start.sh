#!/bin/sh
dovecot
postfix start
python3 /srv/zimbraweb/zimbra_milter.py