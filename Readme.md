# SMTP-Zimbraweb-Bridge in Docker

This Container allows users to send E-Mails via SMTP to a Zimbra Web Interface. It utilizes Postfix as receiver and the python package [zimbraweb](https://github.com/cirosec-studis/python-zimbra-web).

<span style="color: red;">This Container is still in development and should not be used in Production environments or for important E-Mails!</span>

‼ Currently it only supports plain SMTP over Port 587, no TLS. **Your password is readable to anyone on the network** <br />
‼ It also only supports Plaintext E-Mails, no Attachments, until this is implemented in zimbraweb.<br />
‼ SMTP will also not return an error if the sending was unsuccessfull, you need to check the Postifx logs to see if it was successful.


## Setup

To start the container use the following command

```
docker run -p 587:587 ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:a.2
```
Optionally mount a logs directory by adding `-v /path/to/logs:/srv/zimbraweb/logs/`.

You can now connect to the container with your SMTP client at localhost:587.
To authenticate, use your Zimbra Webclient login credentials (without the @domain.tld part!).

### Outlook

In Outlook, you should set your default mail format to "Plain Text" ("Nur Text") by going to File->Options->Mail ("Datei->Optionen->E-mail") and selecting "Plain Text" ("Nur Text") in the "Compose messages in this format" ("Nachrichten in diesem Format verfassen") dropdown.

### Thunderbird

In Thunderbird you should go to Acccount Settings, select "Composition & Addressing" in the Account and deselect "Compose messages in HTML format."

### Other clients

You need to make sure your client sends emails in text/plain because Zimbra Web does not support HTML emails.
