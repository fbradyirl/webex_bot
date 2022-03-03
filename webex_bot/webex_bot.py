"""Main module."""
import logging
import os

import backoff
import coloredlogs
import requests

from webex_bot.commands.echo import EchoCommand
from webex_bot.commands.help import HelpCommand
from webex_bot.exceptions import BotException
from webex_bot.formatting import quote_info
from webex_bot.models.command import CALLBACK_KEYWORD_KEY
from webex_bot.models.response import Response
from webex_bot.websockets.webex_websocket_client import WebexWebsocketClient, DEFAULT_DEVICE_URL

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
                 device_url=DEFAULT_DEVICE_URL):
        """
        Initialise WebexBot.

        @param teams_bot_token: Your token.
        @param approved_users: List of email address who are allowed to chat to this bot.
        @param approved_domains: List of domains which are allowed to chat to this bot.
        """

        log.info("Registering bot with Webex cloud")
        WebexWebsocketClient.__init__(self,
                                      teams_bot_token,
                                      on_message=self.process_incoming_message,
                                      on_card_action=self.process_incoming_card_action,
                                      device_url=device_url)

        # A dictionary of commands this bot listens to
        # Each key in the dictionary is a command, with associated help
        # text and callback function
        # By default supports 2 command, echo and help

        self.help_command = HelpCommand()
        self.commands = {
            EchoCommand(),
            self.help_command
        }
        self.help_command.commands = self.commands

        self.card_callback_commands = {}
        self.approved_users = approved_users
        self.approved_domains = approved_domains
        # Set default help message
        self.help_message = "Hello!  I understand the following commands:  \n"
        self.approval_parameters_check()
        self.bot_display_name = ""
        self.get_me_info()

    @backoff.on_exception(backoff.expo, requests.exceptions.ConnectionError)
    def get_me_info(self):
        """
        Fetch me info from webexteamssdk
        """
        me = self.teams.people.me()
        self.bot_display_name = me.displayName
        log.info(f"Running as bot '{me.displayName}' with email {me.emails}")

    def add_command(self, command_class):
        """
        Add a new command to the bot
        :param command: The command string, example "/status"
        :param help_message: A Help string for this command
        :param callback: The function to run when this command is given
        :return:
        """
        self.commands.add(command_class)

    def approval_parameters_check(self):
        """
        Simply logs a warning if no approved users or domains are set.
        """
        if len(self.approved_users) == 0 and len(self.approved_domains) == 0:
            log.warning("Your bot is open to anyone on Webex Teams. "
                        "Consider limiting this to specific users or domains via the "
                        "WebexBot(approved_domains=['example.com'], approved_users=['user@company.com']) "
                        "bot parameters.")

    def check_user_approved(self, user_email):
        """
        A user is approved if they are in an approved domain or the approved_users list.

        * If both those lists are empty, the user is approved.

        Throws BotException if user is not approved.

        @param user_email: The email from the user of the incoming message.
        """
        user_approved = False
        self.approval_parameters_check()

        if len(self.approved_users) == 0 and len(self.approved_domains) == 0:
            user_approved = True
        elif len(self.approved_domains) > 0 and user_email.split('@')[1] in self.approved_domains:
            user_approved = True
        elif len(self.approved_users) > 0 and user_email in self.approved_users:
            user_approved = True

        if not user_approved:
            log.warning(f"{user_email} is not approved to interact with bot. Ignoring.")
        return user_approved

    def process_incoming_card_action(self, attachment_actions, activity):
        """
        Process an incoming card action, determine the command and action,
        and determine reply.
        :param attachment_actions: The attachment_actions object
        :param activity: The websocket activity object
        :return:
        """
        raw_message = attachment_actions.inputs.get(CALLBACK_KEYWORD_KEY)
        logging.debug(f"raw_message (callback) ={raw_message}")

        self.process_raw_command(raw_message, attachment_actions, activity['actor']['emailAddress'], activity,
                                 is_card_command=True)

    def process_incoming_message(self, teams_message, activity):
        """
        Process an incoming message, determine the command and action,
        and determine reply.
        :param teams_message: The teams_message object
        :param activity: The websocket activity object
        :return:
        """
        user_email = teams_message.personEmail
        raw_message = teams_message.text
        is_one_on_one_space = 'ONE_ON_ONE' in activity['target']['tags']

        if activity['actor']['type'] != 'PERSON':
            logging.debug('message is from a bot, ignoring')
            return

        # Log details on message
        log.info(f"Message from {user_email}: {teams_message}")

        if not self.check_user_approved(user_email=user_email):
            return

        # Remove the Bots display name from the message is this is not a 1-1
        if not is_one_on_one_space:
            raw_message = raw_message.replace(self.bot_display_name, '').strip()

        self.process_raw_command(raw_message, teams_message, user_email, activity)

    def process_raw_command(self, raw_message, teams_message, user_email, activity, is_card_command=False):
        room_id = teams_message.roomId
        is_one_on_one_space = 'ONE_ON_ONE' in activity['target']['tags']

        # Find the command that was sent, if any
        command = self.help_command

        for c in self.commands:
            if not is_card_command:
                if raw_message.lower().find(c.command_keyword) != -1:
                    command = c
                    log.debug("Found command: " + command.command_keyword)
                    # If a command was found, stop looking for others
                    break
            else:
                if raw_message.lower() == c.command_keyword or raw_message.lower() == c.card_callback_keyword:
                    command = c
                    log.debug("Found command: " + command.command_keyword)

        # Build the reply to the user
        reply = ""
        reply_one_to_one = False

        if not is_card_command and command.card is not None:
            response = Response()
            response.text = "This bot requires a client which can render cards."
            response.attachments = {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": command.card
            }
            reply = response
        else:
            message_without_command = WebexBot.get_message_passed_to_command(command.command_keyword, raw_message)
            log.debug(f"Going to run command: '{command}' with input: '{message_without_command}'")
            reply, reply_one_to_one = self.run_command_and_handle_bot_exceptions(command=command,
                                                                                 message=message_without_command,
                                                                                 teams_message=teams_message,
                                                                                 activity=activity)

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

    def run_command_and_handle_bot_exceptions(self, command, message, teams_message, activity):
        try:
            return command.card_callback(message, teams_message, activity), False
        except BotException as e:
            log.warn(f"BotException: {e.debug_message}")
            return e.reply_message, e.reply_one_to_one

    @staticmethod
    def get_message_passed_to_command(command, message):
        """
        Remove the command from the start of the message

        :param command: command string
        :param message: message string
        :return: message without command prefix
        """

        if message.lower().startswith(command.lower()):
            return message[len(command):]
        return message
