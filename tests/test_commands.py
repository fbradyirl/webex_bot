import types

from webex_bot.commands.echo import EchoCommand, EchoCallback
from webex_bot.commands.help import HelpCommand, HELP_COMMAND_KEYWORD
from webex_bot.models.command import Command, COMMAND_KEYWORD_KEY
from webex_bot.models.response import Response


class SimpleCommand(Command):
    def __init__(self, keyword, help_message="Help me"):
        super().__init__(command_keyword=keyword, help_message=help_message)

    def execute(self, message, attachment_actions, activity):
        return "ok"


def test_echo_command_returns_response():
    command = EchoCommand()
    response = command.execute("ignored", None, {})
    assert isinstance(response, Response)
    assert response.attachments[0]["contentType"] == "application/vnd.microsoft.card.adaptive"


def test_echo_callback_uses_input_text():
    command = EchoCallback()
    attachment_actions = types.SimpleNamespace(inputs={"message_typed": "hello"})
    result = command.execute("", attachment_actions, {})
    assert "hello" in result


def test_echo_command_pre_execute_returns_response():
    command = EchoCommand()
    response = command.pre_execute("", types.SimpleNamespace(inputs={}), {})
    assert isinstance(response, Response)


def test_help_command_builds_actions_excluding_help():
    help_command = HelpCommand(bot_name="Bot", bot_help_subtitle="Help", bot_help_image="https://example.com/image.png")
    other_command = SimpleCommand(keyword="ping", help_message="Ping")
    help_command.commands = {help_command, other_command}
    actions, hints = help_command.build_actions_and_hints(thread_parent_id="thread-1")
    assert len(actions) == 1
    assert actions[0].data[COMMAND_KEYWORD_KEY] == "ping"
    assert actions[0].data["thread_parent_id"] == "thread-1"
    assert len(hints) == 1


def test_help_command_keyword_constant():
    assert HELP_COMMAND_KEYWORD == "help"
