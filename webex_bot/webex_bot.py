"""Main module."""
import logging
import coloredlogs
import os

from webex_bot.exceptions import BotException
from webex_bot.formatting import quote_info
from webex_bot.models.response import Response
from webex_bot.websockets.webex_websocket_client import WebexWebsocketClient

log = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"),
                    fmt='%(asctime)s  [%(levelname)s]  '
                        '[%(module)s.%(name)s.%(funcName)'
                        's]:%(lineno)s %(message)s')


class WebexBot(WebexWebsocketClient):

    def __init__(self,
                 teams_bot_token,
                 approved_users=[],
                 approved_domains=[],
                 default_action="/help"):

        log.info("Registering bot with cloud")
        WebexWebsocketClient.__init__(self,
                                      teams_bot_token,
                                      on_message=self.process_incoming_message)

        # A dictionary of commands this bot listens to
        # Each key in the dictionary is a command, with associated help
        # text and callback function
        # By default supports 2 command, /echo and /help
        self.commands = {
            "/echo": {
                "help": "Reply back with the same message sent.",
                "callback": self.send_echo,
            },
            "/help": {"help": "Get help.", "callback": self.send_help},
        }
        self.default_action = default_action
        self.me = self.teams.people.me()
        self.bot_display_name = self.me.displayName
        self.approved_users = approved_users
        self.approved_domains = approved_domains
        # Set default help message
        self.help_message = "Hello!  I understand the following commands:  \n"

    def add_command(self, command, help_message, callback):
        """
        Add a new command to the bot
        :param command: The command string, example "/status"
        :param help_message: A Help string for this command
        :param callback: The function to run when this command is given
        :return:
        """
        self.commands[command.lower()] = {"help": help_message,
                                          "callback": callback}

    def process_incoming_message(self, teams_message, activity):
        """
        Process an incoming message, determine the command and action,
        and determine reply.
        :param teams_message: The teams_message object
        :param activity: The websocket activity object
        :return:
        """
        room_id = teams_message.roomId
        user_email = teams_message.personEmail
        raw_message = teams_message.text
        is_one_on_one_space = 'ONE_ON_ONE' in activity['target']['tags']
        # Log details on message
        log.debug("Message from: " + user_email)

        if activity['actor']['type'] != 'PERSON':
            logging.debug('message is from a bot, ignoring')
            return

        # Check if user is approved
        if len(self.approved_users) > 0 and user_email not in self.approved_users:
            # User NOT approved
            log.error(f"{user_email} is not approved to interact with bot. Ignoring.")
            return "Unapproved user"

        # Remove the Bots display name from the message is this is not a 1-1
        if not is_one_on_one_space:
            raw_message = raw_message.replace(self.bot_display_name, '').strip()

        # Find the command that was sent, if any
        command = ""
        for c in sorted(self.commands.items()):
            # TODO: Remove all mentionedPeople
            if raw_message.find(c[0]) != -1:
                command = c[0]
                log.debug("Found command: " + command)
                # If a command was found, stop looking for others
                break

        # Build the reply to the user
        reply = ""
        reply_one_to_one = False

        # Take action based on command
        # If no command found, send the default_action
        if command in [""] and self.default_action:
            reply = self.commands[self.default_action]["callback"](raw_message, teams_message)
        elif command in self.commands.keys():
            message_without_command = WebexBot.get_message_passed_to_command(command, raw_message)
            log.debug(f"Going to run command: '{command}' with input: '{message_without_command}'")
            reply, reply_one_to_one = self.run_command_and_handle_bot_exceptions(command=command,
                                                                                 message=message_without_command,
                                                                                 teams_message=teams_message)
        else:
            pass

        # allow command handlers to craft their own Teams message
        if reply and isinstance(reply, Response):
            # If the Response lacks a roomId, set it to the incoming room
            if not reply.roomId:
                reply.roomId = room_id
            reply = reply.as_dict()
            self.teams.messages.create(**reply)
            reply = "ok"
        # Support returning a list of Responses
        elif reply and isinstance(reply, list):
            for response in reply:
                # Make sure is a Response
                if isinstance(response, Response):
                    if not response.roomId:
                        response.roomId = room_id
                    self.teams.messages.create(**response.as_dict())
                else:
                    # Just a plain message
                    self.send_message_to_room_or_person(user_email,
                                                        room_id,
                                                        reply_one_to_one,
                                                        is_one_on_one_space,
                                                        response)
            reply = "ok"
        elif reply:
            self.send_message_to_room_or_person(user_email,
                                                room_id,
                                                reply_one_to_one,
                                                is_one_on_one_space,
                                                reply)
        return reply

    def send_message_to_room_or_person(self,
                                       user_email,
                                       room_id,
                                       reply_one_to_one,
                                       is_one_on_one_space,
                                       reply):
        default_move_to_one_to_one_heads_up = \
            quote_info(f"{user_email} I've messaged you 1-1. Please reply to me there.")
        if reply_one_to_one:
            if not is_one_on_one_space:
                self.teams.messages.create(roomId=room_id,
                                           markdown=default_move_to_one_to_one_heads_up)
            self.teams.messages.create(toPersonEmail=user_email,
                                       markdown=reply)
        else:
            self.teams.messages.create(roomId=room_id, markdown=reply)

    def run_command_and_handle_bot_exceptions(self, command, message, teams_message):
        try:
            return self.commands[command]["callback"](message, teams_message), False
        except BotException as e:
            log.warn(f"BotException: {e.debug_message}")
            return e.reply_message, e.reply_one_to_one

    # *** Default Commands included in Bot
    def send_help(self, message, teams_message):
        """
        Construct a help message for users.
        :param message: message with command already stripped
        :param teams_message: teams_message object
        :return:
        """
        message = self.help_message
        for c in sorted(self.commands.items()):
            if c[1]["help"][0] != "*":
                message += "* **%s** %s \n" % (c[0], c[1]["help"])
        return message

    def send_echo(self, message, teams_message):
        """
        Sample command function that just echos back the sent message
        :param message: message with command already stripped
        :param teams_message: teams_message object
        :return:
        """
        return message

    @staticmethod
    def get_message_passed_to_command(command, message):
        """
        Remove the command from the start of the message

        :param command: command string
        :param message: message string
        :return: message without command prefix
        """

        return message.removeprefix(command).strip()
