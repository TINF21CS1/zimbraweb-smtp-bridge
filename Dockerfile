FROM alpine:latest

# Install dependencies
#RUN apk add --no-cache --update postfix ca-certificates socat acme.sh bash && \
RUN apk add --no-cache --update postfix ca-certificates

# Expose smtp port
EXPOSE 25

#postfix config
RUN postconf -e mynetworks=0.0.0.0/0
RUN postconf -e "maillog_file=/dev/stdout"

#add script execution
#https://contrid.net/server/mail-servers/postfix-catch-all-pipe-to-script
RUN echo "@student.dhbw-mannheim.de nobody@student.dhbw-mannheim.de" > /etc/postfix/virtual_aliases
RUN echo "student.dhbw-mannheim.de  zimbrawebtransport:" > /etc/postfix/transport
#not needed when texthash RUN postmap /etc/postfix/virtual_aliases
#not needed when texthash RUN postmap /etc/postfix/transport
#zusammen mit -e muss bei echo $ escaped werden
RUN echo -e "zimbrawebtransport   unix  -       n       n       -       -       pipe\n  flags=FR user=nobody argv=/srv/zimbraweb/send_mail.py\n  \${nexthop} \${user}" >> /etc/postfix/master.cf
RUN echo -e "transport_maps = texthash:/etc/postfix/transport\nvirtual_alias_maps = texthash:/etc/postfix/virtual_aliases" >> /etc/postfix/main.cf

#install python
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

#install git
RUN apk add git

#install zimbraweb package from Github Repo
RUN pip3 install git+https://github.com/cirosec-studis/python-zimbra

#copy python script
ADD ./files/send_mail.py /srv/zimbraweb/send_mail.py
RUN chmod 777 /srv/zimbraweb/send_mail.py

CMD ["postfix", "start-fg"]