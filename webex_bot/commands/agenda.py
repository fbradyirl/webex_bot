import logging

from webex_bot.cards.agenda_card import AGENDA_CARD_CONTENT
from webex_bot.models.command import Command

log = logging.getLogger(__name__)


class AgendaCommand(Command):

    def __init__(self):
        super().__init__(
            command_keyword="agenda",
            help_message="Demo agenda card.",
            card=AGENDA_CARD_CONTENT)

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
