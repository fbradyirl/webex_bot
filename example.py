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
bot = WebexBot(teams_bot_token=os.getenv("WEBEX_TEAMS_ACCESS_TOKEN"),
               approved_rooms=['06586d8d-6aad-4201-9a69-0bf9eeb5766e'],
               bot_name="My Teams Ops Bot",
               include_demo_commands=True,
               proxies=proxies)

# Add new commands for the bot to listen out for.
bot.add_command(EchoCommand())

# Call `run` for the bot to wait for incoming messages.
bot.run()
