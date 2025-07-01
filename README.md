# Introduction

[![Pypi](https://img.shields.io/pypi/v/webex_bot.svg)](https://pypi.python.org/pypi/webex_bot) [![Build Status](https://github.com/fbradyirl/webex_bot/workflows/Python%20package/badge.svg)](https://github.com/fbradyirl/webex_bot/actions)

> [!IMPORTANT]
> This repository is only sporadically maintained. Breaking API changes will be maintained on a best efforts basis.
>
> Collaborators are welcome, as are PRs for enhancements.
>
> Bug reports unrelated to API changes may not get the attention you want.


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
* Uses the [webexpythonsdk][2] package to send back replies from the bot.

## 🚀 Getting started

---

### ✨ Sample Project

You can find a sample project, using OpenAI/ChatGPT with this library here: https://github.com/fbradyirl/openai_bot

----

**Only Python 3.13 is tested at this time.**

1. Install this module from pypi:

`pip install webex_bot`

If you need optional proxy support, use this command instead:

`pip install webex_bot[proxy]`

2. On the Webex Developer portal, create a new [bot token][3] and expose it as an environment variable.

```sh
export WEBEX_ACCESS_TOKEN=<your bots token>
```

3. Run your script:

`python example.py`

See [example.py][4] for details:

```python
import os

from webex_bot.commands.echo import EchoCommand
from webex_bot.webex_bot import WebexBot

# (Optional) Proxy configuration
# Supports https or wss proxy, wss prioritized.
proxies = {
    'https': 'http://proxy.esl.example.com:80',
    'wss': 'socks5://proxy.esl.example.com:1080'
}

# Create a Bot Object
bot = WebexBot(teams_bot_token=os.getenv("WEBEX_ACCESS_TOKEN"),
               approved_rooms=['06586d8d-6aad-4201-9a69-0bf9eeb5766e'],
               bot_name="My Teams Ops Bot",
               include_demo_commands=True,
               proxies=proxies)

# Add new commands for the bot to listen out for.
bot.add_command(EchoCommand())

# Call `run` for the bot to wait for incoming messages.
bot.run()
```

where EchoCommand is defined as:

```python
import logging

from webexpythonsdk.models.cards import Colors, TextBlock, FontWeight, FontSize, Column, AdaptiveCard, ColumnSet, \
    Text, Image, HorizontalAlignment
from webexpythonsdk.models.cards.actions import Submit

from webex_bot.formatting import quote_info
from webex_bot.models.command import Command
from webex_bot.models.response import response_from_adaptive_card

log = logging.getLogger(__name__)


class EchoCommand(Command):

    def __init__(self):
        super().__init__(
            command_keyword="echo",
            help_message="Echo Words Back to You!",
            chained_commands=[EchoCallback()])

    def pre_execute(self, message, attachment_actions, activity):
        """
        (optional function).
        Reply before running the execute function.

        Useful to indicate the bot is handling it if it is a long running task.

        :return: a string or Response object (or a list of either). Use Response if you want to return another card.
        """

        image = Image(url="https://i.postimg.cc/2jMv5kqt/AS89975.jpg")
        text1 = TextBlock("Working on it....", weight=FontWeight.BOLDER, wrap=True, size=FontSize.DEFAULT,
                          horizontalAlignment=HorizontalAlignment.CENTER, color=Colors.DARK)
        text2 = TextBlock("I am busy working on your request. Please continue to look busy while I do your work.",
                          wrap=True, color=Colors.DARK)
        card = AdaptiveCard(
            body=[ColumnSet(columns=[Column(items=[image], width=2)]),
                  ColumnSet(columns=[Column(items=[text1, text2])]),
                  ])

        return response_from_adaptive_card(card)

    def execute(self, message, attachment_actions, activity):
        """
        If you want to respond to a submit operation on the card, you
        would write code here!

        You can return text string here or even another card (Response).

        This sample command function simply echos back the sent message.

        :param message: message with command already stripped
        :param attachment_actions: attachment_actions object
        :param activity: activity object

        :return: a string or Response object (or a list of either). Use Response if you want to return another card.
        """

        text1 = TextBlock("Echo", weight=FontWeight.BOLDER, size=FontSize.MEDIUM)
        text2 = TextBlock("Type in something here and it will be echo'd back to you. How useful is that!",
                          wrap=True, isSubtle=True)
        input_text = Text(id="message_typed", placeholder="Type something here", maxLength=30)
        input_column = Column(items=[input_text], width=2)

        submit = Submit(title="Submit",
                        data={
                            "callback_keyword": "echo_callback"})

        card = AdaptiveCard(
            body=[ColumnSet(columns=[Column(items=[text1, text2], width=2)]),
                  ColumnSet(columns=[input_column]),
                  ], actions=[submit])

        return response_from_adaptive_card(card)


class EchoCallback(Command):

    def __init__(self):
        super().__init__(
            card_callback_keyword="echo_callback",
            delete_previous_message=True)

    def execute(self, message, attachment_actions, activity):
        return quote_info(attachment_actions.inputs.get("message_typed"))
```

4. Now, just interact 1-1 with the bot. Send it a message with the text:

`echo`

and off you go!

# Help

* If you are a Cisco employee, and find this useful, consider sending me a [Connected Recognition][8] (cec: `fibrady`) 🙂
* Also, join the [discussion space here][7].
* Alternatively, open an issue or PR with a question on usage.

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

### 0.2.18 (2022-03-11)

* Remove pyadaptivecards as it is actually built into [webexteamssdk][2]
* Add options for bot name, help message etc.

### 0.2.19 (2022-03-14)

* Bug fix Thanks @muhammad-rafi

### 0.2.20 (2022-04-07)

* Fix for [#6][i6]
* Fix for [#20][i20]
* Use system SSL context when connecting websocket.

### 0.2.21 (2022-04-07)

* Fix for [#13][i13] - Update websockets lib to latest.

### 0.2.22 (2022-04-11)

* Allow for commands to only respond if you are in the approved space.

### 0.3.0 (2022-04-26)

* Add `chained_commands` as a parameter of Command. This allows multiple related cards to be added at once.
* Updated Echo to use Adaptive Card objects (instead of JSON/Dict blob)
* Added docs for some function params.

### 0.3.1 (2022-04-26)

* Fix old school dict cards

### 0.3.3 (2022-06-07)

* Update [webexteamssdk][2] to latest release.

### 0.3.4 (2022-11-01)

* Auto re-connect on websockets.exceptions.ConnectionClosedOK

### 0.4.0 (2023-April-03)

* Bot will reply in response to the original message via the thread ID. This is not always possible in the case of a
  card action response due to some server side issue.

### 0.4.1 (2023-Sept-07)

* Always ensure there is a thread ID in the Activity before accessing it

### 0.4.6 (2024-Apr-24)

* ❌ Bad release. Please do not use this one as there is a startup issue with it.

### 0.5.0 (2024-Apr-25)

* Add max backoff time ([#55][pr55])
* Attached files. Help, threading and log level overrides. ([#54][pr54])
* add stop() call to gracefully exit the bot ([#42][pr42])
* feat(20231212): add help image size parameter ([#46][pr46])
* update websockets to 11.0.3 ([#43][pr43])
* Fix for help_command syntax issue

### 0.5.1 (2024-Apr-25)

* Add Proxy Support. ([#56][pr56])

### 0.5.2 (2024-Aug-21)

* Introduce exact_command_keyword_match feature ([#59][pr59])

### 0.6.0 (2025-Apr-24)

* Migrate from "webexteamssdk" library to "webexpythonsdk" library ([#62][pr62])
* Updated webexpythonsdk library version ([#69][pr69])
* Added support for generators ([#71][pr71])

#### Breaking changes for the existing webex_bot based applications:

* Support is limited to only Python 3.10+ versions. webex_bot applications running on lower Python versions will have to
  adapt to this change in Python version requirement.
* Make the following code changes to your webex_bot application to adapt to ```webex_bot 0.6.0 version and upwards```.

1. ***Mandatory step:*** Replace all imports from `webexteamssdk` to `webexpythonsdk`. For example:
```
from webexteamssdk.models.cards import TextBlock
```
to
```
from webexpythonsdk.models.cards import TextBlock\
```
2. ***This step is applicable only if you pass your Webex bot access token to webex_bot via environment variable:*** Change your Webex bot access token environment variable from `WEBEX_TEAMS_ACCESS_TOKEN` to `WEBEX_ACCESS_TOKEN`. Also, make the following code change in your webex_bot application:
```
bot = WebexBot(teams_bot_token=os.getenv("WEBEX_TEAMS_ACCESS_TOKEN")
```
to
```
bot = WebexBot(teams_bot_token=os.getenv("WEBEX_ACCESS_TOKEN")
```


### 0.6.1 (2025-May-19)

* Handle and retry on InvalidStatusCode in Websocket loop

### 0.6.2 (2025-May-23)

* Fix for [issue #48][i48] - Fix for `Commands not being received` issue.

### 1.0.3 (2025-Jun-04)

* Add connection headers to requests.
* Only call me people API once per run.

### 1.0.4 (2025-Jul-01)

* Add retry mechanism with backoff for websocket 404 errors
*

[1]: https://github.com/aaugustin/websockets

[2]: https://github.com/WebexCommunity/WebexPythonSDK

[3]: https://developer.webex.com/docs/bots

[4]: https://github.com/fbradyirl/webex_bot/blob/main/example.py

[5]: https://www.webex.com

[6]: https://github.com/CiscoSE/pyadaptivecards

[7]: https://eurl.io/#TeBLqZjLs

[8]: https://www.globoforce.net/microsites/t/awards/Redeem?client=cisco&setCAG=true

[pr43]: https://github.com/fbradyirl/webex_bot/pull/43

[pr46]: https://github.com/fbradyirl/webex_bot/pull/46

[pr42]: https://github.com/fbradyirl/webex_bot/pull/42

[pr54]: https://github.com/fbradyirl/webex_bot/pull/54

[pr55]: https://github.com/fbradyirl/webex_bot/pull/55

[pr56]: https://github.com/fbradyirl/webex_bot/pull/56

[pr59]: https://github.com/fbradyirl/webex_bot/pull/59

[pr62]: https://github.com/fbradyirl/webex_bot/pull/62

[pr69]: https://github.com/fbradyirl/webex_bot/pull/69

[pr71]: https://github.com/fbradyirl/webex_bot/pull/71

[i1]: https://github.com/fbradyirl/webex_bot/issues/1

[i2]: https://github.com/fbradyirl/webex_bot/issues/2

[i6]: https://github.com/fbradyirl/webex_bot/issues/6

[i13]: https://github.com/fbradyirl/webex_bot/issues/13

[i20]: https://github.com/fbradyirl/webex_bot/issues/20

[i48]: https://github.com/fbradyirl/webex_bot/issues/48
