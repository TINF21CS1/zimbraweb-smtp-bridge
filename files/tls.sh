#!/bin/sh

certfile=/tls/cert.pem
keyfile=/tls/key.pem

if [ ! -f "$certfile" ]; then
    # generate a self signed certificate (valid for 10 years)
    echo "$(date +"%b %d %H:%M:%S") $HOSTNAME start.sh/tls.sh[$$]: No certfile found, generating new self-signed cert..."
    openssl req -x509 -newkey rsa:4096 -keyout $keyfile -out $certfile -sha256 -days 3650 -nodes -subj "/CN=$HOSTNAME" &>/dev/null
    echo "$(date +"%b %d %H:%M:%S") $HOSTNAME start.sh/tls.sh[$$]: Writing new private key to '$certfile'"
fi

chmod 600 $certfile
chmod 600 $keyfile

echo "$(date +"%b %d %H:%M:%S") $HOSTNAME start.sh/tls.sh[$$]: Writing Postfix conf for TLS"
postconf -e myhostname=$HOSTNAME
postconf -e "smtpd_tls_cert_file = ${certfile}"
postconf -e "smtpd_tls_key_file = ${keyfile}"
postconf -e 'smtp_tls_security_level = may'
postconf -e 'smtpd_tls_security_level = may'
postconf -e 'smtp_tls_note_starttls_offer = yes'
postconf -e 'smtpd_tls_loglevel = 1'
postconf -e 'smtpd_tls_received_header = yes'

postfix stop
postfix start