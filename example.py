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
        is_one_on_one_space = 'ONE_ON_ONE' in activity['target']['tags']

    :return: a string. Or a List of strings. If you return a list of strings, each will be sent in
    an individual reply to the user.
    """
    return message


# Add new commands to the box.
bot.add_command("/echo", "Send me back the message I sent you as a demo.", send_echo)

bot.run()
