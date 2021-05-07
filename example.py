import os

from webex_bot.commands.agenda import AgendaCommand
from webex_bot.webex_bot import WebexBot

# Create a Bot Object
bot = WebexBot(teams_bot_token=os.getenv("WEBEX_TEAMS_ACCESS_TOKEN"))

# Add new commands for the bot to listen out for.
bot.add_command(AgendaCommand())

# Call `run` for the bot to wait for incoming messages.
bot.run()
