FROM alpine:latest

# Install dependencies
#RUN apk add --no-cache --update postfix ca-certificates socat acme.sh bash && \
RUN apk add --no-cache --update postfix dovecot ca-certificates

#install python
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

#install zimbraweb package from Github Repo
RUN pip3 install zimbraweb


#postfix config
RUN postconf -e mynetworks=0.0.0.0/0
RUN postconf -e "maillog_file=/dev/stdout"
RUN postconf -e smtpd_sasl_path=private/auth
RUN postconf -e smtpd_sasl_type=dovecot
RUN postconf -e smtpd_sasl_auth_enable=yes
RUN postconf -e smtpd_delay_reject=yes
RUN postconf -e smtpd_client_restrictions=permit_sasl_authenticated,reject

#add script execution
#https://contrid.net/server/mail-servers/postfix-catch-all-pipe-to-script
RUN touch /etc/postfix/virtual_aliases
RUN echo "*  zimbrawebtransport:" > /etc/postfix/transport
#not needed when texthash RUN postmap /etc/postfix/virtual_aliases
#not needed when texthash RUN postmap /etc/postfix/transport
#zusammen mit -e muss bei echo $ escaped werden
RUN echo -e "zimbrawebtransport   unix  -       n       n       -       -       pipe\n  flags=FR user=nobody argv=/srv/zimbraweb/send_mail.py\n  \${nexthop} \${user} \${sasl_username}" >> /etc/postfix/master.cf
RUN echo -e "transport_maps = texthash:/etc/postfix/transport\nvirtual_alias_maps = texthash:/etc/postfix/virtual_aliases" >> /etc/postfix/main.cf

RUN echo -e "submission inet n - y - - smtpd" >> /etc/postfix/master.cf
RUN echo -e " -o syslog_name=postfix/submission" >> /etc/postfix/master.cf
RUN echo -e " -o smtpd_sasl_auth_enable=yes" >> /etc/postfix/master.cf
RUN echo -e " -o smtpd_sasl_path=private/auth" >> /etc/postfix/master.cf
RUN echo -e " -o smtpd_client_restrictions=permit_sasl_authenticated,reject" >> /etc/postfix/master.cf

#dovecot config
ADD ./files/dovecot/conf.d/10-auth.conf /etc/dovecot/conf.d/10-auth.conf
ADD ./files/dovecot/conf.d/10-master.conf /etc/dovecot/conf.d/10-master.conf
ADD ./files/dovecot/conf.d/auth-checkpassword.conf.ext /etc/dovecot/conf.d/auth-checkpassword.conf.ext

ADD ./files/zimbra_authentication.py /srv/zimbraweb/zimbra_authentication.py
RUN chmod +x /srv/zimbraweb/zimbra_authentication.py

# TODO: this should probably be instead chown postfix:postfix and rwx------? not sure
RUN chmod 777 /srv/zimbraweb/zimbra_authentication.py

#copy python script
ADD ./files/send_mail.py /srv/zimbraweb/send_mail.py
RUN chmod 777 /srv/zimbraweb/send_mail.py

# optionally mount this folder onto the host to get access to some log files, for debugging
RUN mkdir /srv/zimbraweb/logs/
RUN chmod 777 /srv/zimbraweb/logs/

# Expose smtp submission port
EXPOSE 587

ADD ./files/start.sh /
RUN chmod +x /start.sh
CMD ["/start.sh"]