# SMTP-Zimbraweb-Bridge in Docker

This Container allows users to send E-Mails via SMTP to a Zimbra Web Interface. It utilizes Postfix as receiver and the python package [zimbraweb](https://github.com/cirosec-studis/python-zimbra-web).

<span style="color: red;">This Container is still in development and should not be used in Production environments or for important E-Mails!</span>

‼ Currently it only supports plain SMTP over Port 25 and one User per Container.<br />
‼ It also only supports Plaintext E-Mails, no Attachments, until this is implemented in zimbraweb.<br />
‼ SMTP will also not return an error if the sending was unsuccessfull, you need to check the Postifx logs to see if it was successful.

## Setup

In this early version, the Container is bound to one user.

Create a folder with the files `user` and `password` that contain exactly those. No newline, no quotations marks.

To start the container use the following command

```
docker run -p 25:25 -v /path/to/secrets:/secrets jmlemmi/zimbrawebbridge:a.1
```