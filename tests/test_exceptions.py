from webex_bot.exceptions import BotException


def test_bot_exception_attributes():
    exc = BotException("debug", "reply", reply_one_to_one=True)
    assert exc.debug_message == "debug"
    assert exc.reply_message == "reply"
    assert exc.reply_one_to_one is True
