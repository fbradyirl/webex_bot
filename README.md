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

from webex_bot.commands.echo import EchoCommand
from webex_bot.webex_bot import WebexBot

# Create a Bot Object
bot = WebexBot(teams_bot_token=os.getenv("WEBEX_TEAMS_ACCESS_TOKEN"),
               approved_rooms=['06586d8d-6aad-4201-9a69-0bf9eeb5766e'])

# Add new commands for the bot to listen out for.
bot.add_command(EchoCommand())

# Call `run` for the bot to wait for incoming messages.
bot.run()
```

where EchoCommand is defined as:

```python
import logging

from webex_bot.cards.echo_card import ECHO_CARD_CONTENT
from webex_bot.formatting import quote_info
from webex_bot.models.command import Command
from webex_bot.cards.busy_card import BUSY_CARD_CONTENT
from webex_bot.models.response import Response

log = logging.getLogger(__name__)


class EchoCommand(Command):

    def __init__(self):
        super().__init__(
            command_keyword="echo",
            help_message="Type in something here and it will be echo'd back to you. How useful is that!",
            card=ECHO_CARD_CONTENT)

    def pre_card_load_reply(self, message, attachment_actions, activity):
        """
        (optional function).
        Reply before sending the initial card.

        Useful if it takes a long time for the card to load.

        :return: a string or Response object (or a list of either). Use Response if you want to return another card.
        """

        response = Response()
        response.text = "This bot requires a client which can render cards."
        response.attachments = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": BUSY_CARD_CONTENT
        }

        # As with all replies, you can send a Response() (card), a string or a list of either or mix.
        return [response, "Sit tight! I going to show the echo card soon."]

    def pre_execute(self, message, attachment_actions, activity):
        """
        (optionol function).
        Reply before running the execute function.

        Useful to indicate the bot is handling it if it is a long running task.

        :return: a string or Response object (or a list of either). Use Response if you want to return another card.
        """
        response = Response()
        response.text = "This bot requires a client which can render cards."
        response.attachments = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": BUSY_CARD_CONTENT
        }

        return response
    def execute(self, message, attachment_actions, activity):
        """
        If you want to respond to a submit operation on the card, you
        would write code here!

        You can return text string here or even another card (Response).

        This sample command function simply echos back the sent message.

        :param message: message with command already stripped
        :param attachment_actions: attachment_actions object
        :param activity: activity object

        :return: a string or Response object. Use Response if you want to return another card.
        """
        email = activity["actor"]['emailAddress']

        return quote_info(attachment_actions.inputs.get("message_typed"))
```

4. Now, just interact 1-1 with the bot. Send it a message with the text:

`echo`

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

### 0.2.2 (2021-05-08)

* Typo fix

### 0.2.3 (2021-05-10)

* Fix no module found error

### 0.2.5 (2021-05-10)

* Pin websockets version

### 0.2.6 (2021-05-21)

* Couple of bug fixes and support python 3.8 fully

### 0.2.7 (2021-09-27)

* Fix for #11 server rejected WebSocket connection: HTTP 404

### 0.2.8 (2022-01-06)

#### Breaking change for existing cards:

* Pass activity down to execute function so attibutes such as email can be fetched from card actions.
* Update your existing `execute` functions to include the extra `activity` parameter.

```python
    def execute(self, message, attachment_actions, activity):
        log.info(
            f"activity={activity} ")
        email = activity["actor"]['emailAddress']
        return quote_info(f"person email is '{email}'")
```

### 0.2.9 (2022-03-03)

* Fixes for #14 & #16

### 0.2.10 (2022-03-03)

* Add new workflow for Github releases.

### 0.2.11 (2022-03-08)

* Add `pre_execute` function to Command. (optional function to overide). Reply before running the execute function.
  Useful to indicate the bot is handling it if it is a long running task.
* See echo.py for example usage.

### 0.2.12 (2022-03-09)

* Check for duplicate card callback keywords and raise exception if one exists.

### 0.2.13 (2022-03-09)

* add support for `pre_card_load_reply` overide. Reply before sending the initial card. Useful if it takes a long time
  for the card to load.

### 0.2.14 (2022-03-09)

* add support for deleting previous card in a chain.

### 0.2.15 (2022-03-09)

* Support for chained cards

### 0.2.16 (2022-03-10)

* Add support for approved rooms.

### 0.2.17 (2022-03-11)

* Add support for using [pyadaptivecards][6]

[1]: https://github.com/aaugustin/websockets

[2]: https://github.com/CiscoDevNet/webexteamssdk

[3]: https://developer.webex.com/docs/bots

[4]: https://github.com/fbradyirl/webex_bot/example.py

[5]: https://www.webex.com

[6]: https://github.com/CiscoSE/pyadaptivecards

[i1]: https://github.com/fbradyirl/webex_bot/issues/1

[i2]: https://github.com/fbradyirl/webex_bot/issues/2
