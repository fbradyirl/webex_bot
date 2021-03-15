class BotException(Exception):
    """Exception which we want to reply to the user about in the bot."""

    def __init__(self, debug_message, reply_message, reply_one_to_one=False):
        """
        Generic exception for handling issues which require a custom message back to the user.
        :param debug_message: Message to log
        :param reply_message: Message to send back to the bot user
        :param reply_one_to_one: Some replies should be private. e.g. auth info. If you
                                 don't want to the reply to be to a space, set this to True.
        """
        self.debug_message = debug_message
        self.reply_message = reply_message
        self.reply_one_to_one = reply_one_to_one

    pass
