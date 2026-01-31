from webex_bot.models.command import Command, CALLBACK_KEYWORD_KEY, COMMAND_KEYWORD_KEY


class SimpleCommand(Command):
    def __init__(self, command_keyword=None, card=None):
        super().__init__(command_keyword=command_keyword, card=card)

    def execute(self, message, attachment_actions, activity):
        return "ok"


def test_command_uses_callback_keyword_from_card():
    card = {
        "actions": [
            {
                "type": "Action.Submit",
                "data": {CALLBACK_KEYWORD_KEY: "cb"},
            }
        ]
    }
    command = SimpleCommand(command_keyword="ping", card=card)
    assert command.card_callback_keyword == "cb"


def test_command_uses_command_keyword_from_card():
    card = {
        "actions": [
            {
                "type": "Action.Submit",
                "data": {COMMAND_KEYWORD_KEY: "cmd"},
            }
        ]
    }
    command = SimpleCommand(command_keyword=None, card=card)
    assert command.command_keyword == "cmd"


def test_command_sets_default_callback_keyword_when_missing():
    card = {
        "actions": [
            {
                "type": "Action.Submit",
                "data": {},
            }
        ]
    }
    command = SimpleCommand(command_keyword="ping", card=card)
    assert command.card_callback_keyword == "callback___ping"
    assert card["actions"][0]["data"][CALLBACK_KEYWORD_KEY] == "callback___ping"
