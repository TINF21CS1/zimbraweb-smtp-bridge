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
RUN echo "@student.dhbw-mannheim.de root@student.dhbw-mannheim.de" > /etc/postfix/virtual_aliases
RUN echo "student.dhbw-mannheim.de  zimbrawebtransport:" > /etc/postfix/transport
RUN postmap /etc/postfix/virtual_aliases
RUN postmap /etc/postfix/transport
#zusammen mit -e muss bei echo $ escaped werden
RUN echo -e "zimbrawebtransport   unix  -       n       n       -       -       pipe\n  flags=FR user=root argv=/srv/send_mail.py\n  \${nexthop} \${user}" >> /etc/postfix/master.cf
RUN echo -e "transport_maps = hash:/etc/postfix/transport\nvirtual_alias_maps = hash:/etc/postfix/virtual_aliases" >> /etc/postfix/main.cf

CMD ["postfix", "start-fg"]