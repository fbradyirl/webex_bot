class Command:
    def __init__(self, command_keyword, help_message, card, card_callback):
        self.command_keyword = command_keyword
        self.help_message = help_message
        self.card = card
        self.card_callback_keyword = None
        if card is not None:
            self.card_callback_keyword = card['actions'][0]['data']['callback_keyword'].lower()
        self.card_callback = card_callback
