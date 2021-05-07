import logging

log = logging.getLogger(__name__)

CALLBACK_KEYWORD_KEY = 'callback_keyword'


class Command:
    def __init__(self, command_keyword, help_message, card):
        self.command_keyword = command_keyword
        self.help_message = help_message
        self.card = card
        self.card_callback = self.execute
        self.card_callback_keyword = None

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

    def execute(self, message, attachment_actions):
        raise NotImplementedError("Hey, Don't forget to override this execute method if you have a submit callback!")
