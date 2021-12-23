FROM alpine:latest

# Install dependencies
RUN apk add --no-cache --update postfix dovecot ca-certificates git gcc musl-dev linux-headers libmilter-dev

#install python
RUN apk add --update --no-cache python3 python3-dev && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip; pip3 install --no-cache --upgrade pip setuptools

RUN pip3 install zimbraweb git+https://github.com/sdgathman/pymilter

#postfix basic config
RUN postconf -e "mynetworks=0.0.0.0/0" "maillog_file=/var/log/log" "smtpd_sasl_path=private/auth" "smtpd_sasl_type=dovecot" "smtpd_sasl_auth_enable=yes" "smtpd_delay_reject=yes" "smtpd_client_restrictions=permit_sasl_authenticated,reject" "smtpd_milters=unix:/milter.sock"
#RUN echo -e "postlog   unix-dgram n  -       n       -       1       postlogd" >> /etc/postfix/master.cf

#postfix transport script execution
RUN echo "*  zimbrawebtransport:" > /etc/postfix/transport
RUN echo -e "zimbrawebtransport   unix  -       n       n       -       -       pipe\n  flags=FR user=nobody argv=/srv/zimbraweb/send_mail.py\n  \${nexthop} \${user} \${sasl_username}" >> /etc/postfix/master.cf
RUN postconf -e "transport_maps=texthash:/etc/postfix/transport"

RUN echo -e "submission inet n - y - - smtpd\n -o syslog_name=postfix/submission\n -o smtpd_sasl_auth_enable=yes\n -o smtpd_sasl_path=private/auth\n -o smtpd_client_restrictions=permit_sasl_authenticated,reject" >> /etc/postfix/master.cf

#dovecot config
ADD ./files/dovecot/conf.d/ /etc/dovecot/conf.d/

#copy python scripts
ADD ./files/*.py /srv/zimbraweb/
RUN chmod 777 /srv/zimbraweb/*.py

RUN mkdir /srv/zimbraweb/mnt/ /srv/zimbraweb/logs/; chmod -R 777 /srv/zimbraweb/mnt/; chmod -R 777 /srv/zimbraweb/logs/

VOLUME /srv/zimbraweb/mnt/

# Add crontab to delete auth tokens from memory
RUN crontab -l /cron
RUN echo "* * * * * find /dev/shm/ -name auth_* -type f -perm 444 -mmin +3 -delete" >> /cron
RUN crontab /cron
RUN rm /cron

# Expose smtp submission port
EXPOSE 587

ADD ./files/start.sh /
RUN chmod +x /start.sh

ADD ./files/tls.sh /
RUN chmod +x /tls.sh; mkdir /tls/

CMD ["/start.sh"]
