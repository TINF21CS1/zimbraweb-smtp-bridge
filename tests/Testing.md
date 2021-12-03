# Environment

Start Postfix Smarthost Relay:
```
docker run -e ALLOWED_SENDER_DOMAINS=student.dhbw-mannheim.de -d boky/postfix
```

Build and start container in one command:
```
docker run -p 587:587 -h zimbra -d $(docker build -q .)
```

Building a container from a different file than `Dockerfile`:
```
docker build --file ./Dockerfile-multi .
```

# Testing

## PS

Powershell for using Send-MailMessage:
```
docker run -it mcr.microsoft.com/powershell

Send-MailMessage -SmtpServer localhost -Port 587 -From s212689@student.dhbw-mannheim.de -To s212689@student.dhbw-mannheim.de -Credential (Get-Credential) -Subject "[Test] Testnachricht" -Body "Dies ist eine Testmessage aus Powershell f03"
```

## Alpine

html eml test file without variables: https://raw.githubusercontent.com/cirosec-studis/zimbraweb-smtp-bridge/feature_smtpfallback/tests/html.eml

Command for sending mail.
```bash
sendmail -f "s212689@student.dhbw-mannheim.de" s212689@student.dhbw-mannheim.de < html.eml
```
-f is "from", the other is the recipient

Sending mail from other instance:
```bash
postmulti -i postfix-zimbra -x sendmail -f "s212689@student.dhbw-mannheim.de" s212689@student.dhbw-mannheim.de < html.eml
```