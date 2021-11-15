#!/bin/sh
echo "NOTE: none of these parameters are verified. If you screw something up, run the script again. If you want to remove TLS you need to reset the container."

read -p 'What domain is this server running on? ' hostname

read -p 'Where is the domain certificate located (within the docker container)? [default: /srv/zimbraweb/ssl_certificate.pem]: ' certfile
certfile=${certfile:-/srv/zimbraweb/ssl_certificate.pem}

read -p 'Where is the private key located (within the docker container)? [default: /srv/zimbraweb/private_key.pem]: ' keyfile
keyfile=${keyfile:-/srv/zimbraweb/private_key.pem}

chmod 777 ${keyfile}
chmod 777 ${certfile}

postconf -e myhostname=$hostname
postconf -e "smtpd_tls_cert_file = ${certfile}"
postconf -e "smtpd_tls_key_file = ${keyfile}"
postconf -e 'smtp_tls_security_level = may'
postconf -e 'smtpd_tls_security_level = may'
postconf -e 'smtp_tls_note_starttls_offer = yes'
postconf -e 'smtpd_tls_loglevel = 1'
postconf -e 'smtpd_tls_received_header = yes'

postfix stop
postfix start