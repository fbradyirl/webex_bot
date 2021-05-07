import logging

from webex_bot.cards.echo_card import ECHO_CARD_CONTENT
from webex_bot.formatting import quote_info
from webex_bot.models.command import Command

log = logging.getLogger(__name__)


class EchoCommand(Command):

    def __init__(self):
        super().__init__(
            command_keyword="echo",
            help_message="Delete orgs under a partner.",
            card=ECHO_CARD_CONTENT)

    def execute(self, message, attachment_actions):
        """
        Sample command function that just echos back the sent message
        :param message: message with command already stripped
        :param attachment_actions: attachment_actions object
        :return:
        """
        return quote_info(attachment_actions.inputs.get("message_typed"))
