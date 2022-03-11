"""Main module."""
import logging
import os

import backoff
import coloredlogs
import requests

from webex_bot.commands.agenda import AgendaCommand
from webex_bot.commands.echo import EchoCommand
from webex_bot.commands.help import HelpCommand
from webex_bot.exceptions import BotException
from webex_bot.formatting import quote_info
from webex_bot.models.command import CALLBACK_KEYWORD_KEY, Command, COMMAND_KEYWORD_KEY
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
                 approved_rooms=[],
                 device_url=DEFAULT_DEVICE_URL,
                 include_demo_commands=True,
                 bot_name="Webex Bot",
                 bot_help_subtitle="Click on a button to begin."):
        """
        Initialise WebexBot.

        @param teams_bot_token: Your token.
        @param approved_users: List of email address who are allowed to chat to this bot.
        @param approved_domains: List of domains which are allowed to chat to this bot.
        @param approved_rooms: List of rooms whose members are allowed to chat to this bot.
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

        self.help_command = HelpCommand(
            bot_name=bot_name,
            bot_help_subtitle=bot_help_subtitle,
            bot_help_image=self.teams.people.me().avatar)
        self.commands = {
            self.help_command
        }
        if include_demo_commands:
            self.command.add(EchoCommand())
            self.command.add(AgendaCommand())

        self.help_command.commands = self.commands

        self.card_callback_commands = {}
        self.approved_users = approved_users
        self.approved_domains = approved_domains
        self.approved_rooms = approved_rooms
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
        log.debug(f"Running as bot '{me}'")

    def add_command(self, command_class: Command):
        """
        Add a new command to the bot
        :param command: The command string, example "/status"
        :param help_message: A Help string for this command
        :param callback: The function to run when this command is given
        :return:
        """

        for c in self.commands:
            log.debug(f"Checking command '{c}' against {command_class}")
            new_callback_keyword = command_class.card_callback_keyword
            if new_callback_keyword and c.card_callback_keyword == new_callback_keyword:
                raise Exception(f"Error adding new command: '{command_class.command_keyword}'. "
                                f"Duplicate callback_keyword found: "
                                f"'{new_callback_keyword}'. Use a unique keyword in your "
                                f"'{command_class.command_keyword}' adaptive card JSON.")

        self.commands.add(command_class)

    def approval_parameters_check(self):
        """
        Simply logs a warning if no approved users, domains or rooms are set.
        """
        if len(self.approved_users) == 0 and len(self.approved_domains) == 0 and len(self.approved_rooms) == 0:
            log.warning("Your bot is open to anyone on Webex Teams. "
                        "Consider limiting this to specific users, domains or room members via the "
                        "WebexBot(approved_domains=['example.com'], approved_users=['user@company.com'], "
                        "approved_rooms=['Y2lzY29zcGFyazovL3VzL1JPT00vZDUwMDE2ZWEtNmQ5My00MTY1LTg0ZWEtOGNmNTNhYjA3YzA5']) "
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

        if len(self.approved_users) == 0 and len(self.approved_domains) == 0 and len(self.approved_rooms) == 0:
            user_approved = True
        elif len(self.approved_domains) > 0 and user_email.split('@')[1] in self.approved_domains:
            user_approved = True
        elif len(self.approved_users) > 0 and user_email in self.approved_users:
            user_approved = True
        elif len(self.approved_rooms) > 0 and self.is_user_member_of_room(user_email, self.approved_rooms):
            user_approved = True

        if not user_approved:
            log.warning(f"{user_email} is not approved to interact with bot. Ignoring.")
        return user_approved

    def is_user_member_of_room(self, user_email, approved_rooms):
        is_user_member = False

        for approved_room in approved_rooms:
            room_members = self.teams.memberships.list(roomId=approved_room, personEmail=user_email)
            for member in room_members:
                if member.personEmail == user_email:
                    is_user_member = True

        return is_user_member

    def process_incoming_card_action(self, attachment_actions, activity):
        """
        Process an incoming card action, determine the command and action,
        and determine reply.
        :param attachment_actions: The attachment_actions object
        :param activity: The websocket activity object
        :return:
        """
        callback_keyword = attachment_actions.inputs.get(CALLBACK_KEYWORD_KEY)
        command_keyword = attachment_actions.inputs.get(COMMAND_KEYWORD_KEY)
        is_card_callback_command = callback_keyword is not None
        raw_message = callback_keyword if callback_keyword else command_keyword
        logging.debug(f"raw_message (callback) ='{raw_message}' is_card_callback_command={is_card_callback_command}")

        self.process_raw_command(raw_message,
                                 attachment_actions, activity['actor']['emailAddress'], activity,
                                 is_card_callback_command=is_card_callback_command)

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

        # Remove the Bots display name from the message if this is not a 1-1
        if not is_one_on_one_space:
            raw_message = raw_message.replace(self.bot_display_name, '').strip()

        self.process_raw_command(raw_message, teams_message, user_email, activity)

    def process_raw_command(self, raw_message, teams_message, user_email, activity, is_card_callback_command=False):
        room_id = teams_message.roomId
        is_one_on_one_space = 'ONE_ON_ONE' in activity['target']['tags']

        # Find the command that was sent, if any
        command = self.help_command

        for c in self.commands:
            user_command = raw_message.lower()
            log.debug("--------")
            log.debug(f"is_card_callback_command: {is_card_callback_command}")
            log.debug(f"user_command: {user_command}")
            log.debug(f"command_keyword: {c.command_keyword}")

            if not is_card_callback_command and c.command_keyword:
                if user_command.find(c.command_keyword) != -1:
                    command = c
                    log.debug(f"Found command: {command.command_keyword}")
                    # If a command was found, stop looking for others
                    break
            else:
                log.debug(f"card_callback_keyword: {c.card_callback_keyword}")
                if user_command == c.command_keyword or user_command == c.card_callback_keyword:
                    command = c
                    log.debug(f"Found command: {command.command_keyword}")
                    break

        # Build the reply to the user
        reply = ""
        reply_one_to_one = False
        message_without_command = WebexBot.get_message_passed_to_command(command.command_keyword, raw_message)

        if command.delete_previous_message and hasattr(teams_message, 'messageId'):
            previous_message_id = teams_message.messageId
            log.info(f"delete_previous_message is True. Deleting message with ID: {previous_message_id}")
            self.teams.messages.delete(previous_message_id)

        if not is_card_callback_command and command.card is not None:
            response = Response()
            response.text = "This bot requires a client which can render cards."
            response.attachments = {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": command.card
            }

            pre_card_load_reply, pre_card_load_reply_one_to_one = self.run_pre_card_load_reply(command=command,
                                                                                               message=message_without_command,
                                                                                               teams_message=teams_message,
                                                                                               activity=activity)
            self.do_reply(pre_card_load_reply, room_id, user_email, pre_card_load_reply_one_to_one, is_one_on_one_space)
            reply = response
        else:
            log.debug(f"Going to run command: '{command}' with input: '{message_without_command}'")
            pre_execute_reply, pre_execute_reply_one_to_one = self.run_pre_execute(command=command,
                                                                                   message=message_without_command,
                                                                                   teams_message=teams_message,
                                                                                   activity=activity)
            self.do_reply(pre_execute_reply, room_id, user_email, pre_execute_reply_one_to_one, is_one_on_one_space)
            reply, reply_one_to_one = self.run_command_and_handle_bot_exceptions(command=command,
                                                                                 message=message_without_command,
                                                                                 teams_message=teams_message,
                                                                                 activity=activity)

        return self.do_reply(reply, room_id, user_email, reply_one_to_one, is_one_on_one_space)

    def do_reply(self, reply, room_id, user_email, reply_one_to_one, is_one_on_one_space):
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

    def run_pre_card_load_reply(self, command, message, teams_message, activity):
        """
        This allows a reply to be sent back before the command/card function is called. Useful if it takes a while for the card to generate.
        """
        try:
            return command.pre_card_load_reply(message, teams_message, activity), False
        except BotException as e:
            log.warn(f"BotException: {e.debug_message}")
            return e.reply_message, e.reply_one_to_one

    def run_pre_execute(self, command, message, teams_message, activity):
        """
        This allows a reply to be sent back before the execute function is called. Useful if it takes a while to run.
        """
        try:
            return command.pre_execute(message, teams_message, activity), False
        except BotException as e:
            log.warn(f"BotException: {e.debug_message}")
            return e.reply_message, e.reply_one_to_one

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

        if command and message.lower().startswith(command.lower()):
            return message[len(command):]
        return message
