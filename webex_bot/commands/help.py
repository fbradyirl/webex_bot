import logging

from webexpythonsdk.models.cards import Colors, TextBlock, FontWeight, FontSize, Column, AdaptiveCard, ColumnSet, \
    ImageSize, Image, Fact
from webexpythonsdk.models.cards.actions import Submit

from webex_bot.models.command import Command, COMMAND_KEYWORD_KEY
from webex_bot.models.response import response_from_adaptive_card

log = logging.getLogger(__name__)

HELP_COMMAND_KEYWORD = "help"


class HelpCommand(Command):

    def __init__(self, bot_name, bot_help_subtitle, bot_help_image, bot_help_image_size=ImageSize.SMALL):
        self.commands = None
        super().__init__(
            command_keyword=HELP_COMMAND_KEYWORD,
            help_message="Get Help",
            card=None)
        self.card_callback = self.build_card
        self.card_populated = False
        self.bot_name = bot_name
        self.bot_help_subtitle = bot_help_subtitle
        self.bot_help_image = bot_help_image
        self.bot_help_image_size = bot_help_image_size

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
        heading = TextBlock(self.bot_name, weight=FontWeight.BOLDER, wrap=True, size=FontSize.LARGE)
        subtitle = TextBlock(self.bot_help_subtitle, wrap=True, size=FontSize.SMALL, color=Colors.LIGHT)

        image = Image(
            url=self.bot_help_image,
            size=self.bot_help_image_size)

        header_column = Column(items=[heading, subtitle], width=2)
        header_image_column = Column(
            items=[image],
            width=1,
        )

        log.info(f"build help card activity: {activity}")
        thread_parent_id = None
        if 'parent' not in activity:
            thread_parent_id = activity['id']

        actions, hint_texts = self.build_actions_and_hints(thread_parent_id)

        card = AdaptiveCard(
            body=[ColumnSet(columns=[header_column, header_image_column]),
                  # ColumnSet(columns=[Column(items=[subtitle])]),
                  # FactSet(facts=hint_texts),
                  ],
            actions=actions)

        return response_from_adaptive_card(adaptive_card=card)

    def build_actions_and_hints(self, thread_parent_id):
        # help_card = HELP_CARD_CONTENT
        help_actions = []
        hint_texts = []

        if self.commands is not None:
            # Sort list by keyword
            sorted_commands_list = sorted(self.commands, key=lambda command: (
                command.command_keyword is not None, command.command_keyword))
            for command in sorted_commands_list:
                if command.help_message and command.command_keyword != HELP_COMMAND_KEYWORD:
                    action = Submit(
                        title=f"{command.help_message}",
                        data={COMMAND_KEYWORD_KEY: command.command_keyword,
                              'thread_parent_id': thread_parent_id},
                    )
                    help_actions.append(action)

                    hint = Fact(title=command.command_keyword,
                                value=command.help_message)

                    hint_texts.append(hint)
        return help_actions, hint_texts
