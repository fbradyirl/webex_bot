import logging

from webex_bot.cards.echo_card import ECHO_CARD_CONTENT
from webex_bot.formatting import quote_info
from webex_bot.models.command import Command

log = logging.getLogger(__name__)


class EchoCommand(Command):

    def __init__(self):
        super().__init__(
            command_keyword="echo",
            help_message="Type in something and it will be echo'd back to you. How useful is that!",
            card=ECHO_CARD_CONTENT)

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
        return quote_info(attachment_actions.inputs.get("message_typed"))
