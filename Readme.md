# Zimbraweb-SMTP-Bridge in Docker

This Container allows users to send E-Mails via SMTP to a Zimbra Web Interface. It utilizes Postfix as receiver and the python package [zimbraweb](https://github.com/cirosec-studis/python-zimbra-web).

<span style="color: red;">This Container is still in development and should not be used in Production environments or for important E-Mails!</span>

‼ Currently it only supports plain SMTP over Port 587, no TLS. **Your password is readable to anyone on the network** <br />
‼ It only supports Plaintext E-Mails, and Attachments, but not HTML or RTF-Mails. This is due to a restriction in the Zimbra Webinterface<br />


## Setup

To start the container use the following command

```
docker run -p 587:587 ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:nightly
```

### Docker Tags

The following tags are available:

* `ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:nightly` - This builds from `main` every night so that changes in the zimbraweb package are pulled into the container. Use this one to stay up to date.
* `ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:latest` - Latest tagged build
* `ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:vX.Y.Z` - Version X.Y.Z (e.g. v1.0.0)
* `ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:develop` - development build



If you're on a raspberry pi, note the section [Docker on Raspberry Pi](#docker-on-raspberry-pi).

Optionally mount a logs directory by adding `-v /path/to/logs:/srv/zimbraweb/logs/`.

You can now connect to the container with your SMTP client at localhost:587.
To authenticate, use your Zimbra Webclient login credentials (without the @domain.tld part!).

### Outlook

In Outlook, you should set your default mail format to "Plain Text" ("Nur Text") by going to File->Options->Mail ("Datei->Optionen->E-mail") and selecting "Plain Text" ("Nur Text") in the "Compose messages in this format" ("Nachrichten in diesem Format verfassen") dropdown.

### Thunderbird

In Thunderbird you should go to Acccount Settings, select "Composition & Addressing" in the Account and deselect "Compose messages in HTML format."

### Other clients

You need to make sure your client sends emails in text/plain because Zimbra Web does not support HTML emails.

### Docker on Raspberry Pi

Note that currently the alpine image does not work on raspberry pi without the following tweak:

```bash
# Get signing keys to verify the new packages, otherwise they will not install
rpi ~$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 04EE7237B7D453EC 648ACFD622F3D138

# Add the Buster backport repository to apt sources.list
rpi ~$ echo 'deb http://httpredir.debian.org/debian buster-backports main contrib non-free' | sudo tee -a /etc/apt/sources.list.d/debian-backports.list

rpi ~$ sudo apt update
rpi ~$ sudo apt install libseccomp2 -t buster-backports
```

This fix is from https://blog.samcater.com/fix-workaround-rpi4-docker-libseccomp2-docker-20/. Alpine requires libseccomp2>2.4.2 but on debian buster has 2.3.6, this fix installes a newer version from the backports repository.
