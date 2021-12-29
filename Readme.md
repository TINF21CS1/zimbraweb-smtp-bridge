# Zimbraweb-SMTP-Bridge in Docker

This Container allows users to send E-Mails via SMTP to a Zimbra Web Interface. It utilizes Postfix as receiver and the python package [zimbraweb](https://github.com/cirosec-studis/python-zimbra-web).

<span style="color: red;">This Container is still in development and should not be used in Production environments or for important E-Mails!</span>

‼ It only supports Plaintext E-Mails, and Attachments, but not HTML or RTF-Mails. This is due to a restriction in the Zimbra Webinterface<br />

## Public Bridge

There is a public server available at dhbw-mannheim.email at port 2525. Connect to it via SMTP with STARTTLS. For increased security we recommend hosting the Bridge yourself if you have a server available, [more on that below](#self-hosting). The public bridge is configured to automatically purge all data every 60 minutes. No logging data is written to disk at all, auth tokens (which are needed to authenticated with the Web Client) are kept only in memory and for 60 minutes at most, but in almost all cases will be deleted immediately after successful email delivery.

You can use the following settings:

IMAP (SSL/TLS): `studgate.dhbw-mannheim.de` at port `993`

SMTP (STARTTLS): `dhbw-mannheim.email` at port `2525`

Authenticate with the same credentials that you use for the Web Interface (--> without the @student.dhbw.mannheim.de part!)

You need to make sure your client sends emails in text/plain because Zimbra Web does not support HTML emails.

### Outlook

https://user-images.githubusercontent.com/18506129/141695204-2dd563d1-2a69-4a9c-97b9-0e1ee1667c24.mp4

In Outlook, you should set your default mail format to "Plain Text" ("Nur Text") by going to File->Options->Mail ("Datei->Optionen->E-mail") and selecting "Plain Text" ("Nur Text") in the "Compose messages in this format" ("Nachrichten in diesem Format verfassen") dropdown.

### Thunderbird

https://user-images.githubusercontent.com/18506129/141694660-e9a54848-7474-45b1-9ffb-956a3e1ee264.mp4

Please note that lowering the minimum TLS version is requried because the Zimbra IMAP server uses outdated IMAP. There is sadly nothing we can do on our side to fix this. The SMTP Bridge uses up-to-date TLS.

In Thunderbird you should go to Acccount Settings, select "Composition & Addressing" in the Account and deselect "Compose messages in HTML format."

## Self-Hosting

To start the container use the following command

```
docker run --name smtp_bridge -p 587:587 ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:nightly
```

If you do not have a domain name associated with the server, you can use whatever hostname you want, e.g. "smtp_bridge.local".

### Configuration

There are two options for configuring. A default configuration will be generated for all values that are not set manually.

The default configuration is as follows:

```json
{
    "zimbra_host": "https://studgate.dhbw-mannheim.de",
    "email_domain": "student.dhbw-mannheim.de",
    "smtp_fallback": "disabled",
    "smtp_fallback_relay_host": "172.17.0.2",
    "log_level": "info",
}
```

#### permitted configuration values

smtp_fallback: enabled, disabled
log_level: *debug* - DEBUG, any other value - INFO

#### config.json

Put a `config.json` file into the mounted folder at `/srv/zimbraweb/mnt/`.

#### ENV variables

In docker ENV variables can be set with the `-e` flag.

Set `ENVCONFIG=true` to enable configuration via ENV Variables. Then set all other ENV-variables to the configuration value you want.

### TLS Support

TLS is enabled by default, using a self-signed certificate for the hostname you provided. This will be enough in most cases, you will just need to accept the self-signed certificate in your email client. Thunderbird and Outlook will tell you that the certificate could not be verified. You will need to add an exception.

#### CA-signed certificates

If you want to use a certificate signed by a Certificate Authority, e.g. Let's Encrypt, you can do that.

You already need to have a certificate and a private key file. You can get them with [`certbot`](https://certbot.eff.org/lets-encrypt/). Usually running `sudo certbot certonly --standalone -d <your-server-domain>` will do the trick. The certificate and key should end up in `/etc/letsencrypt/live/<your-server-domain>/fullchain.pem` and `/etc/letsencrypt/live/<your-server-domain>/privkey.pem`.

Make sure to run the docker container with the same hostname as the certificate you are using.

Put the certificate and key into a folder on your host and name them `cert.pem` and `key.pem` respectively.

Then you can use the following command to start the container with the certificate and key you just created:

```
docker run -v /host/path/to/tls/folder/:/tls/ --name smtp_bridge -h <your_domain_name> -p 587:587 ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:nightly
```

That's it, the container will now use the signed TLS certificate.

### Docker Tags

The following tags are available:

* `ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:nightly` - This builds from `main` every night so that changes in the zimbraweb package are pulled into the container. Use this one to stay up to date.
* `ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:latest` - Latest tagged build
* `ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:vX.Y.Z` - Version X.Y.Z (e.g. v1.0.0)
* `ghcr.io/cirosec-studis/zimbraweb-smtp-bridge:develop` - development build

If you're on a raspberry pi, note the section [Docker on Raspberry Pi](#docker-on-raspberry-pi).

You can now connect to the container with your SMTP client at localhost:587.
To authenticate, use your Zimbra Webclient login credentials (without the @domain.tld part!).

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

### SMTP Relay function

Zimbra has certain limitations, like not supporting html Emails. If you want to route these unsupported E-Mails via another SMTP relay, use this function. It is disabled by default.

❗ be careful with this option. It can lead to your Mail being classified as Spam or outright rejected by the receiving Server due to wrong Origin.

If you want to take the easy option use the `docker-compose.yml` provided in this repository.

Set the `smtp_fallback` configuration option to `"enabled"` and `smtp_fallback_relay_host` to a Mailserver that accepts Mail on Port 25.

### Known Limitations

* Currently authentication to the Relay host is not supported.
* Naming the Container after the Mail-Domain of the Zimbra Server or any other Domain, that may be the recipient of actual Mail is not supported and will lead to errors in delivering mail. (See #34)
