import types

import pytest

from webex_bot.models.command import Command
from webex_bot.models.response import Response
from webex_bot.exceptions import BotException
from webex_bot.webex_bot import WebexBot


class DummyCommand(Command):
    def __init__(self, command_keyword="ping", exact_match=False, card_callback_keyword=None):
        super().__init__(
            command_keyword=command_keyword,
            exact_command_keyword_match=exact_match,
            help_message="Ping command",
            card_callback_keyword=card_callback_keyword,
        )

    def execute(self, message, attachment_actions, activity):
        return "pong"


class PreExecuteCommand(Command):
    def __init__(self, command_keyword="work", delete_previous_message=False):
        super().__init__(
            command_keyword=command_keyword,
            help_message="Pre execute",
            delete_previous_message=delete_previous_message,
        )

    def pre_execute(self, message, attachment_actions, activity):
        return "Working"

    def execute(self, message, attachment_actions, activity):
        return "Done"


class ExceptionCommand(Command):
    def __init__(self, command_keyword="fail"):
        super().__init__(
            command_keyword=command_keyword,
            help_message="Failing command",
        )

    def pre_execute(self, message, attachment_actions, activity):
        raise BotException("debug", "pre-reply", reply_one_to_one=True)

    def execute(self, message, attachment_actions, activity):
        raise BotException("debug", "reply", reply_one_to_one=False)


def test_get_message_passed_to_command():
    assert WebexBot.get_message_passed_to_command("help", "help me") == " me"
    assert WebexBot.get_message_passed_to_command("help", "hello") == "hello"


def test_check_user_approved_unrestricted(bot):
    assert bot.check_user_approved("user@example.com", approved_rooms=[]) is True


def test_check_user_approved_domain(bot):
    bot.approved_domains = ["example.com"]
    assert bot.check_user_approved("user@example.com", approved_rooms=[]) is True
    assert bot.check_user_approved("user@other.com", approved_rooms=[]) is False


def test_check_user_approved_room_membership(bot):
    assert bot.check_user_approved("member@example.com", approved_rooms=["room-1"]) is True
    assert bot.check_user_approved("outsider@example.com", approved_rooms=["room-1"]) is False


def test_add_command_duplicate_callback_keyword_raises(bot):
    first = DummyCommand(command_keyword="first", card_callback_keyword="dup")
    second = DummyCommand(command_keyword="second", card_callback_keyword="dup")
    bot.add_command(first)
    with pytest.raises(Exception):
        bot.add_command(second)


def test_process_incoming_message_ignores_other_bot(bot, teams_message, one_on_one_activity):
    bot.allow_bot_to_bot = False
    teams_message.personEmail = "otherbot@example.com"
    activity = dict(one_on_one_activity)
    activity["actor"]["type"] = "BOT"
    bot.process_incoming_message(teams_message, activity)
    assert bot.teams.messages.created == []


def test_process_incoming_message_runs_help(bot, teams_message, one_on_one_activity):
    teams_message.text = "unknown"
    bot.process_incoming_message(teams_message, one_on_one_activity)
    assert len(bot.teams.messages.created) >= 1


def test_do_reply_with_response_sets_room_id(bot):
    response = Response()
    response.markdown = "hi"
    bot.do_reply(response, "room-1", "user@example.com", False, True, "thread-1")
    assert bot.teams.messages.created[-1]["roomId"] == "room-1"


def test_do_reply_with_response_list(bot):
    response = Response()
    response.markdown = "hello"
    bot.do_reply([response], "room-1", "user@example.com", False, True, "thread-1")
    assert bot.teams.messages.created[-1]["roomId"] == "room-1"


def test_process_raw_command_exact_match(bot, teams_message, one_on_one_activity):
    command = DummyCommand(command_keyword="ping", exact_match=True)
    bot.add_command(command)
    bot.process_raw_command("ping", teams_message, "user@example.com", one_on_one_activity)
    assert bot.teams.messages.created[-1]["markdown"] == "pong"


def test_process_raw_command_callback(bot, one_on_one_activity):
    command = DummyCommand(command_keyword="ping", card_callback_keyword="ping_cb")
    bot.add_command(command)
    attachment_actions = types.SimpleNamespace(
        inputs={"callback_keyword": "ping_cb"},
        roomId="room-1",
    )
    activity = dict(one_on_one_activity)
    activity["actor"]["emailAddress"] = "user@example.com"
    bot.process_incoming_card_action(attachment_actions, activity)
    assert bot.teams.messages.created[-1]["markdown"] == "pong"


def test_process_raw_command_delete_previous_message(bot, teams_message, one_on_one_activity):
    command = PreExecuteCommand(delete_previous_message=True)
    bot.add_command(command)
    bot.process_raw_command("work", teams_message, "user@example.com", one_on_one_activity)
    assert teams_message.messageId in bot.teams.messages.deleted
    assert "message-1" in bot.teams.messages.deleted


def test_run_pre_execute_handles_bot_exception(bot, teams_message, one_on_one_activity):
    command = ExceptionCommand()
    reply, one_to_one = bot.run_pre_execute(command, "msg", teams_message, one_on_one_activity)
    assert reply == "pre-reply"
    assert one_to_one is True


def test_run_command_and_handle_bot_exceptions(bot, teams_message, one_on_one_activity):
    command = ExceptionCommand()
    reply, one_to_one = bot.run_command_and_handle_bot_exceptions(command, "msg", teams_message, one_on_one_activity)
    assert reply == "reply"
    assert one_to_one is False
