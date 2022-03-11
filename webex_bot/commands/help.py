import logging

from pyadaptivecards.actions import Submit
from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.components import TextBlock, Column, Image
from pyadaptivecards.container import ColumnSet
from pyadaptivecards.options import FontWeight, FontSize, ImageSize

from webex_bot.models.command import Command, COMMAND_KEYWORD_KEY
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
        heading = TextBlock("Ops Bot", weight=FontWeight.BOLDER, size=FontSize.LARGE)

        # Bot Avatar. Todo: read this from the bot user payload.
        image = Image(
            url="https://avatar-prod-us-east-2.webexcontent.com/Avtr~V1~1eb65fdf-9643-417f-9974-ad72cae0e10f/V1~4a3d9c4fa69e22b8c10b55e4f9ac15633e4e7e9c2e60a9424e8c122b378304ff~5fe5663c77434517b5ec460cb064762e~80",
            size=ImageSize.SMALL)

        header_column = Column(items=[heading], width=2)
        header_image_column = Column(
            items=[image],
            width=1,
        )
        actions, hint_texts = self.build_actions_and_hints()
        hints_column = Column(items=hint_texts)

        card = AdaptiveCard(
            body=[ColumnSet(columns=[header_column, header_image_column]),
                  ColumnSet(columns=[hints_column])],
            actions=actions)

        response = Response()
        response.text = "This bot requires a client which can render cards."
        response.attachments = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": card.to_dict()
        }

        return response

    def build_actions_and_hints(self):
        # help_card = HELP_CARD_CONTENT
        help_actions = []
        hint_texts = []

        if self.commands is not None:
            # Sort list by keyword
            sorted_commands_list = sorted(self.commands, key=lambda command: (
                command.command_keyword is not None, command.command_keyword))
            for command in sorted_commands_list:
                if command.help_message:
                    action = Submit(
                        title=command.command_keyword,
                        data={COMMAND_KEYWORD_KEY: command.command_keyword}
                    )
                    help_actions.append(action)

                    hint = TextBlock(f"**{command.command_keyword}** {command.help_message}",
                                     weight=FontWeight.LIGHTER,
                                     wrap=True,
                                     size=FontSize.SMALL)

                    hint_texts.append(hint)
        return help_actions, hint_texts
