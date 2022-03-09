import logging

from webex_bot.cards.agenda_card import AGENDA_CARD_CONTENT
from webex_bot.cards.busy_card import BUSY_CARD_CONTENT
from webex_bot.models.command import Command
from webex_bot.models.response import Response

log = logging.getLogger(__name__)


class AgendaCommand(Command):

    def __init__(self):
        super().__init__(
            command_keyword="agenda",
            help_message="Demo agenda card.",
            card=AGENDA_CARD_CONTENT)

    def pre_card_load_reply(self, message, attachment_actions, activity):
        """
        (optional function).
        Reply before sending the initial card.

        Useful if it takes a long time for the card to load.

        :return: a string or Response object (or a list of either). Use Response if you want to return another card.
        """

        response = Response()
        response.text = "This bot requires a client which can render cards."
        response.attachments = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": BUSY_CARD_CONTENT
        }

        # As with all replies, you can send a Response() (card), a string or a list of either or mix.
        return [response, "Sit tight! I am looking up your agenda."]

    def execute(self, message, attachment_actions, activity):
        """
        If you want to respond to a submit operation on the card, you
        would write code here!

        See echo.py as an example.

        You can return text string here or even another card (Response).

        :param message: message with command already stripped
        :param attachment_actions: attachment_actions object
        :param activity: activity object

        :return:
        """
        pass
