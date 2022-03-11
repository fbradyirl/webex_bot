import logging
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)

CALLBACK_KEYWORD_KEY = 'callback_keyword'
COMMAND_KEYWORD_KEY = "command_keyword"


class Command(ABC):
    def __init__(self, command_keyword=None, card=None, help_message=None, delete_previous_message=False,
                 card_callback_keyword=None):
        self.command_keyword = command_keyword
        self.help_message = help_message
        self.card = card
        self.pre_card_callback = self.execute
        self.card_callback = self.execute
        self.card_callback_keyword = card_callback_keyword
        self.delete_previous_message = delete_previous_message

        # Now, if this card has a Action.Submit action, let's read the callback keyword,
        # or if it doesnt exist, add it.
        # Only work from the first action for now. Maybe in future support multiple actions.
        if card is not None:
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
