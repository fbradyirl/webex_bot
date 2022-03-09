import os

from webex_bot.commands.echo import EchoCommand
from webex_bot.webex_bot import WebexBot

# Create a Bot Object
bot = WebexBot(teams_bot_token=os.getenv("WEBEX_TEAMS_ACCESS_TOKEN"),
               approved_rooms=["Y2lzY29zcGFyazovL3VzL1JPT00vMzZmZDU1YzAtOWZkNy0xMWVjLTkwZmQtYjU5MzAyZWRlOWQ1"])

# Add new commands for the bot to listen out for.
#bot.add_command(EchoCommand())

# Call `run` for the bot to wait for incoming messages.
bot.run()
