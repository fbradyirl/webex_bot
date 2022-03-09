import logging

from webex_bot.cards.busy_card import BUSY_CARD_CONTENT
from webex_bot.cards.echo_card import ECHO_CARD_CONTENT
from webex_bot.formatting import quote_info
from webex_bot.models.command import Command
from webex_bot.models.response import Response

log = logging.getLogger(__name__)


class EchoCommand(Command):

    def __init__(self):
        super().__init__(
            command_keyword="echo",
            help_message="Type in something and it will be echo'd back to you. How useful is that!",
            card=ECHO_CARD_CONTENT)

    def pre_execute(self, message, attachment_actions, activity):
        """
        (optional function).
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

        :return: a string or Response object (or a list of either). Use Response if you want to return another card.
        """
        return quote_info(attachment_actions.inputs.get("message_typed"))
