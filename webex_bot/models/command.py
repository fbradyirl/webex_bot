import logging

log = logging.getLogger(__name__)

CALLBACK_KEYWORD_KEY = 'callback_keyword'


class Command:
    def __init__(self, command_keyword, help_message, card, card_callback):
        self.command_keyword = command_keyword
        self.help_message = help_message
        self.card = card
        self.card_callback = card_callback
        self.card_callback_keyword = None
        if card is not None:
            try:
                self.card_callback_keyword = card['actions'][0]['data'][CALLBACK_KEYWORD_KEY].lower()
                log.info(f"self.card_callback_keyword={self.card_callback_keyword}")
            except Exception:
                log.error("You must ensure your hard has a 'callback_keyword' entry defined under "
                          "'actions'>'data'>'callback_keyword'. Without this, the bot cannot process data submitted from this card to"
                          f" card_callback={self.card_callback}")
