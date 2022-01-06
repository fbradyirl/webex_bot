import logging

from webex_bot.cards.help_card import HELP_CARD_CONTENT
from webex_bot.models.command import Command
from webex_bot.models.response import Response

log = logging.getLogger(__name__)


class HelpCommand(Command):

    def __init__(self):
        self.commands = None
        super().__init__(
            command_keyword="help",
            help_message="Get Help",
            card=None)
        self.card_callback = self.build_card
        self.card_populated = False

    def execute(self, message, attachment_actions, activity):
        pass

    def build_card(self, message, attachment_actions, activity):
        """
        Construct a help message for users.
        :param message: message with command already stripped
        :param attachment_actions: attachment_actions object
        :param activity: activity object
        :return:
        """
        response = Response()
        response.text = "This bot requires a client which can render cards."
        response.attachments = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": self.help_card_with_commands()
        }

        return response

    def help_card_with_commands(self):
        help_card = HELP_CARD_CONTENT

        if self.commands is not None:
            if not self.card_populated:
                # Sort list by keyword
                sorted_commands_list = sorted(self.commands, key=lambda command: command.command_keyword)
                for command in sorted_commands_list:
                    help_card['body'].append({
                        "type": "TextBlock",
                        "text": f"**{command.command_keyword}** {command.help_message}",
                        "fontType": "Monospace",
                        "wrap": True,
                    })
                self.card_populated = True
            return help_card
        return "I'm of no help at all."
