FROM alpine:latest

#install python
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

#install zimbraweb package from Github Repo
RUN pip3 install git+https://github.com/cirosec-studis/python-zimbra

#copy python script
ADD ./files/send_mail.py /srv/zimbraweb/send_mail.py

#inspired by https://xc2.wb1.xyz/post/how-to-run-a-postfix-mail-server-in-a-docker-container/

#install postfix
RUN apk add --no-cache --update postfix cyrus-sasl ca-certificates bash && \
    apk add --no-cache --upgrade musl musl-utils && \
    # Clean up
    (rm "/tmp/"* 2>/dev/null || true) && (rm -rf /var/cache/apk/* 2>/dev/null || true)

#copy required config files for postfix
ADD ./files/aliases /etc/aliases

EXPOSE 25

# Mark used folders
VOLUME [ "/var/spool/postfix", "/etc/postfix" ]

# Configure Postfix on startup
COPY ./files/docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]

# Start postfix in foreground mode
CMD ["postfix", "start-fg"]