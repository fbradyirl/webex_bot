# Introduction

[![Pypi](https://img.shields.io/pypi/v/webex_bot.svg)](https://pypi.python.org/pypi/webex_bot) [![Build Status](https://github.com/fbradyirl/webex_bot/workflows/Python%20package/badge.svg)](https://github.com/fbradyirl/webex_bot/workflows/)

![Pipeline](https://github.com/fbradyirl/webex_bot/workflows/.github/workflows/main.yml/badge.svg)


Python package for a Webex Bot based on websockets.

* Uses the [websocket][1] module to receive incoming messages, thus avoiding the need
  to have a public IP for incoming webhooks.
* Uses the [webexteamssdk][2] package to send back replies from the bot.

This is licensed under the MIT license.

## Features

* Receive incoming messages without having to run ngrok or similar.
* Send replies based on your defined 'commands'.

## Getting started

1. Install this module:

`pip install webex_bot`

2. On the Webex Developer portal, create a new [bot token][3] and expose it as an environment variable.

```sh
export WEBEX_TEAMS_ACCESS_TOKEN=<your bots token>
```

3. Run the bot:

```python
import os
from webex_bot.webex_bot import WebexBot

# Create a Bot Object
bot = WebexBot(teams_bot_token=os.getenv("WEBEX_TEAMS_ACCESS_TOKEN"))


def send_echo(message, teams_message):
    """
    Sample command function that just echos back the sent message
    :param message: message with command already stripped
    :param teams_message: teams_message object. Get more info about the message received from this. e.g.

        room_id = teams_message.roomId
        user_email = teams_message.personEmail
        raw_message = teams_message.text

    :return: a string. Or a List of strings. If you return a list of strings, each will be sent in
    an individual reply to the user.
    """
    return message


# Add new commands to the box.
bot.add_command("/echo", "Send me back the message I sent you as a demo.", send_echo)

bot.run()
```
See `example.py`

[1]: https://github.com/aaugustin/websockets

[2]: https://github.com/CiscoDevNet/webexteamssdk

[3]: https://developer.webex.com/docs/bots
