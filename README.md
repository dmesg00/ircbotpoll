`ircbotpoll` - IRC Bot for creating polls

## Install (Debian-based system):

```
# apt update
# apt install python3 python3-venv python3-pip
# mkdir -p /opt/ircbotpoll
# wget -c "https://q3aql.dev/scripts/ircbotpoll.py" -O /opt/ircbotpoll/ircbotpoll.py
# python3 -m venv /opt/ircbotpoll
# source /opt/ircbotpoll/bin/activate
# pip install --upgrade pip
# pip install irc
# useradd -m -s /bin/bash ircbot
# chown ircbot:ircbot -R /opt/ircbotpoll
```

## Edit configuration:

```                                                                                                                                                                                                                  
# vim /opt/ircbotpoll/ircbotpoll.py                                                                                                                                                                       
```  

Replace these lines with your configuration:

```
######## CONFIGURATION (Edit with your settings)
SERVER   = "localhost"
PORT     = 6667
USE_TLS  = False
NICK     = "history-bot"
REALNAME = "IRC Message History"
CHANNELS = ["#support", "#linux"]
#########
```

## Add the bot at system startup:

Create the file `/etc/systemd/system/ircbotpoll.service` with the following:

```
[Unit]
Description=IRC history bot
After=network.target

[Service]
Type=simple
User=ircbot
Group=ircbot
WorkingDirectory=/opt/ircbotpoll
Environment=PATH=/opt/ircbotpoll/bin
ExecStart=/opt/ircbotpoll/bin/python3 /opt/ircbotpoll/ircbotpoll.py
Restart=on-failure
RestartSec=5s
KillMode=process

[Install]
WantedBy=multi-user.target
```

Add the service at startup and start it:

```
# systemctl daemon-reload
# systemctl enable ircbotpoll
# systemctl start ircbotpoll
```

## Syntax:

```

!poll <question>
!vote <option>
!results
!endpoll
```

## How to uninstall:

```
# rm -rf /opt/ircbotpoll
# rm -rf /etc/system/system/ircbotpoll.service
# deluser ircbot
```

## Dependencies
* python3
* python3-irc
* python3-pip

