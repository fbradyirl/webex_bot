# Introduction

[![Pypi](https://img.shields.io/pypi/v/webex_bot.svg)](https://pypi.python.org/pypi/webex_bot) [![Build Status](https://github.com/fbradyirl/webex_bot/workflows/Python%20package/badge.svg)](https://github.com/fbradyirl/webex_bot/actions)

By using this module, you can create a [Webex Teams][5] messaging bot quickly in just a couple of lines of code.

This module does not require you to set up an ngrok tunnel to receive incoming messages when behind a firewall or
inside a LAN. This package instead uses a websocket to receive messages from the Webex cloud.

## Features

* Uses the [websockets][1] module to receive incoming messages, thus avoiding the need to have a public IP or use
  incoming webhooks.
* Simply add 'commands' which are just strings which instruct the bot to perform some action and reply with some result.
* Allows for single or multi-post responses. This is useful if you want to reply with a lot of data, but it won't all
  fit in a single response.
* Restrict bot to certain users or domains.
* Uses the [webexteamssdk][2] package to send back replies from the bot.

## Getting started

1. Install this module from pypi:

`pip install webex_bot`

2. On the Webex Developer portal, create a new [bot token][3] and expose it as an environment variable.

```sh
export WEBEX_TEAMS_ACCESS_TOKEN=<your bots token>
```

3. Run your script:

`python example.py`

See [example.py][4] for details:

```python
import os

from webex_bot.commands.agenda import AgendaCommand
from webex_bot.webex_bot import WebexBot

# Create a Bot Object
bot = WebexBot(teams_bot_token=os.getenv("WEBEX_TEAMS_ACCESS_TOKEN"))

# Add new commands for the bot to listen out for.
bot.add_command(AgendaCommand())

# Call `run` for the bot to wait for incoming messages.
bot.run()

```

4. Now, just interact 1-1 with the bot. Send it a message with the text:

`echo` or `agenda`

and off you go!

# History

### 0.1.2 (2021-03-15)

* First release on PyPI.

### 0.1.4 (2021-03-23)

* Better retry on websocket connection failure
* Added support for approved domains
* Other cleanup

### 0.1.5 (2021-03-23)

* Retry websocket connection on socket.gaierror. ([#1][i1])

### 0.1.6 (2021-03-25)

* Send ack on websocket message received. ([#2][i2])

### 0.1.7 (2021-03-26)

* Minor cleanup.
* Log bot email on startup.

### 0.1.8 (2021-05-04)

* Fetch incoming message ID as base64.

### 0.2.0 (2021-05-07)

* Switch format entirely to use cards.

### 0.2.1 (2021-05-07)

* Import fix

[1]: https://github.com/aaugustin/websockets

[2]: https://github.com/CiscoDevNet/webexteamssdk

[3]: https://developer.webex.com/docs/bots

[4]: example.py

[5]: https://www.webex.com

[i1]: https://github.com/fbradyirl/webex_bot/issues/1

[i2]: https://github.com/fbradyirl/webex_bot/issues/2
