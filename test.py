import os

from webex_bot.commands.echo import EchoCommand
from webex_bot.webex_bot import WebexBot

# Create a Bot Object
bot = WebexBot(teams_bot_token='YTYzOGRjNTMtNzQ1OS00YzIyLTg1OTctZDE1ZTBlZjNkOTExNWJhNWVmYjctZjUz_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f',
               approved_rooms=[],
               bot_name="My Teams Ops Bot",
               include_demo_commands=True)

# Add new commands for the bot to listen out for.
bot.add_command(EchoCommand())

# Call `run` for the bot to wait for incoming messages.
bot.run()