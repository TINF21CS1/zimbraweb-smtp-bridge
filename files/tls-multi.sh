#!/bin/sh

certfile=/tls/cert.pem
keyfile=/tls/key.pem

if [ ! -f "$certfile" ]; then
    # generate a self signed certificate (valid for 10 years)
    openssl req -x509 -newkey rsa:4096 -keyout $keyfile -out $certfile -sha256 -days 3650 -nodes -subj "/CN=$HOSTNAME"
fi

chmod 600 $certfile
chmod 600 $keyfile

postconf -c /etc/postfix-zimbra/ -e myhostname=$HOSTNAME
postconf -c /etc/postfix-zimbra/ -e "smtpd_tls_cert_file = ${certfile}"
postconf -c /etc/postfix-zimbra/ -e "smtpd_tls_key_file = ${keyfile}"
postconf -c /etc/postfix-zimbra/ -e 'smtp_tls_security_level = may'
postconf -c /etc/postfix-zimbra/ -e 'smtpd_tls_security_level = may'
postconf -c /etc/postfix-zimbra/ -e 'smtp_tls_note_starttls_offer = yes'
postconf -c /etc/postfix-zimbra/ -e 'smtpd_tls_loglevel = 1'
postconf -c /etc/postfix-zimbra/ -e 'smtpd_tls_received_header = yes'

postmulti -i postfix-zimbra -p stop
postmulti -i postfix-zimbra -p start