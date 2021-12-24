#!/bin/sh
python3 /srv/zimbraweb/zimbra_config.py
/tls.sh
dovecot
echo "$(date +"%b %d %H:%M:%S") $HOSTNAME start.sh[$$]: Started dovecot."
postfix start
crond
echo "$(date +"%b %d %H:%M:%S") $HOSTNAME start.sh[$$]: Started crond."
python3 /srv/zimbraweb/zimbra_milter.py &
sleep 2
echo "$(date +"%b %d %H:%M:%S") $HOSTNAME start.sh[$$]: ➔ Switching to log output from '/var/log/log'"
echo "$(date +"%b %d %H:%M:%S") $HOSTNAME start.sh[$$]: System is now operational and ready to receive E-Mails" > /var/log/log
tail -f /var/log/log