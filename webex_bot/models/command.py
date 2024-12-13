import logging
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)

CALLBACK_KEYWORD_KEY = 'callback_keyword'
COMMAND_KEYWORD_KEY = "command_keyword"


class Command(ABC):

    def __init__(self, command_keyword=None, exact_command_keyword_match=False,
                 chained_commands=[], card=None,
                 help_message=None, delete_previous_message=False,
                 card_callback_keyword=None, approved_rooms=None):
        """
        Create a new bot command.

        If the command has a simple string keyword, it can be invoked by the user when they type that word.

        Alternatively, if `card_callback_keyword` is defined, the command can be invoked from the 'callback_keyword'
         data from the Submit action of a previous card. E.g.

            Submit(title="Submit", data={
                    "callback_keyword": "echo_callback"}
                    )

        @param command_keyword: (optional) Text indicating a phrase to invoke this card.
        @param exact_command_keyword_match: If True, there will be an exact command_keyword match performed. If False, then a sub-string match will be performed. Default: False. 
        @param chained_commands: (optional) List of other commands related
        to this command. This allows multiple related cards to be added at once.
        @param card: (deprecated) A dict representation of the JSON card.
        Prefer to use cards built in code using the webexpythonsdk.models.cards classes
        (see https://github.com/fbradyirl/webex_bot/blob/main/webex_bot/commands/echo.py for example)
        @param help_message: Short description of this command.
        @param delete_previous_message: If True, the card which invoked this command will be deleted. (default False)
        @param card_callback_keyword: (optional) this command can be invoked from the 'callback_keyword'
         text in the data from the Submit action of a previous card.
        @param approved_rooms: If defined, only members of these spaces will be allowed to run this command. Default: None (everyone)
        """
        self.command_keyword = command_keyword
        self.exact_command_keyword_match = exact_command_keyword_match
        self.help_message = help_message
        self.card = card
        self.pre_card_callback = self.execute
        self.card_callback = self.execute
        self.card_callback_keyword = card_callback_keyword
        self.delete_previous_message = delete_previous_message
        self.approved_rooms = approved_rooms
        self.chained_commands = chained_commands

        # Now, if this card has a Action.Submit action, let's read the callback keyword,
        # or if it doesnt exist, add it.
        # Only work from the first action for now. Maybe in future support multiple actions.
        if card is not None:
            log.warning(f"[{command_keyword}]. Using a card dict is now deprecated. "
                        f"Switch to use adaptive cards built in code "
                        "using the webexpythonsdk.models.cards classes (see "
                        "https://github.com/fbradyirl/webex_bot/blob/main/webex_bot/commands/echo.py for example)")
            if 'actions' in card:
                if len(card['actions']) > 0:
                    first_action = card['actions'][0]
                    if 'type' in first_action and first_action['type'] == 'Action.Submit':
                        if 'data' in first_action and len(first_action['data']) > 0:
                            data = first_action['data']
                            if CALLBACK_KEYWORD_KEY in data:
                                self.card_callback_keyword = first_action['data'][CALLBACK_KEYWORD_KEY]
                            elif COMMAND_KEYWORD_KEY in data:
                                self.command_keyword = first_action['data'][COMMAND_KEYWORD_KEY]
                            else:
                                log.warning(
                                    f"card actions data but no entry for '{CALLBACK_KEYWORD_KEY}' for {command_keyword}")
                                self.set_default_card_callback_keyword()
                        else:
                            log.warning(
                                f"no card actions data so no entry for '{CALLBACK_KEYWORD_KEY}' for {command_keyword}")
                            self.set_default_card_callback_keyword()
                else:
                    log.info(f"No actions defined in this card. command_keyword={command_keyword}")

    def set_default_card_callback_keyword(self):
        if self.card_callback_keyword is None:
            if 'data' not in self.card['actions'][0]:
                self.card['actions'][0]['data'] = {}

            self.card_callback_keyword = f"callback___{self.command_keyword}"
            self.card['actions'][0]['data'][CALLBACK_KEYWORD_KEY] = self.card_callback_keyword

            log.info(
                f"Added default action for '{self.command_keyword}' {CALLBACK_KEYWORD_KEY}={self.card_callback_keyword}")

    def pre_card_load_reply(self, message, attachment_actions, activity):
        pass

    def pre_execute(self, message, attachment_actions, activity):
        pass

    @abstractmethod
    def execute(self, message, attachment_actions, activity):
        pass
