import asyncio
import json
import logging
import socket
import ssl
import uuid

import backoff
import certifi
import requests
import websockets
from webexteamssdk import WebexTeamsAPI

logger = logging.getLogger(__name__)

DEFAULT_DEVICE_URL = "https://wdm-a.wbx2.com/wdm/api/v1"

DEVICE_DATA = {
    "deviceName": "pywebsocket-client",
    "deviceType": "DESKTOP",
    "localizedModel": "python",
    "model": "python",
    "name": "python-spark-client",
    "systemName": "python-spark-client",
    "systemVersion": "0.1"
}

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


class WebexWebsocketClient(object):
    def __init__(self,
                 access_token,
                 device_url=DEFAULT_DEVICE_URL,
                 on_message=None,
                 on_card_action=None):
        self.access_token = access_token
        self.teams = WebexTeamsAPI(access_token=access_token)
        self.device_url = device_url
        self.device_info = None
        self.on_message = on_message
        self.on_card_action = on_card_action
        self.websocket = None

    def _process_incoming_websocket_message(self, msg):
        """
        Handle websocket data.
        :param msg: The raw websocket message
        """
        if msg['data']['eventType'] == 'conversation.activity':
            activity = msg['data']['activity']
            if activity['verb'] == 'post':
                logger.debug(f"activity={activity}")

                message_base_64_id = self._get_base64_message_id(activity)
                webex_message = self.teams.messages.get(message_base_64_id)
                logger.debug(f"webex_message from message_base_64_id: {webex_message}")
                if self.on_message:
                    # ack message first
                    self._ack_message(message_base_64_id)
                    # Now process it with the handler
                    self.on_message(teams_message=webex_message, activity=activity)
            elif activity['verb'] == 'cardAction':
                logger.debug(f"activity={activity}")

                message_base_64_id = self._get_base64_message_id(activity)
                attachment_actions = self.teams.attachment_actions.get(message_base_64_id)
                logger.info(f"attachment_actions from message_base_64_id: {attachment_actions}")
                if self.on_card_action:
                    # ack message first
                    self._ack_message(message_base_64_id)
                    # Now process it with the handler
                    self.on_card_action(attachment_actions=attachment_actions, activity=activity)
            else:
                logger.debug(f"activity verb is: {activity['verb']} ")

    def _get_base64_message_id(self, activity):
        """
        In order to geo-locate the correct DC to fetch the message from, you need to use the base64 Id of the
        message.
        @param activity: incoming websocket data
        @return: base 64 message id
        """
        activity_id = activity['id']
        logger.debug(f"activity verb=post. message id={activity_id}")
        conversation_url = activity['target']['url']
        conv_target_id = activity['target']['id']
        verb = "messages" if activity['verb'] == "post" else "attachment/actions"
        conversation_message_url = conversation_url.replace(f"conversations/{conv_target_id}",
                                                            f"{verb}/{activity_id}")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        conversation_message = requests.get(conversation_message_url,
                                            headers=headers).json()
        logger.debug(f"conversation_message={conversation_message}")
        return conversation_message['id']

    def _ack_message(self, message_id):
        """
        Ack that this message has been processed. This will prevent the
        message coming again.
        @param message_id: activity message 'id'
        """
        logger.debug(f"WebSocket ack message with id={message_id}")
        ack_message = {'type': 'ack',
                       'messageId': message_id}
        asyncio.run(self.websocket.send(json.dumps(ack_message)))
        logger.info(f"WebSocket ack message with id={message_id}. Complete.")

    def _get_device_info(self, check_existing=True):
        """
        Get device info from Webex Cloud.

        If it doesn't exist, one will be created.
        """
        if check_existing:
            logger.debug('Getting device list')
            try:
                resp = self.teams._session.get(f"{self.device_url}/devices")
                for device in resp['devices']:
                    if device['name'] == DEVICE_DATA['name']:
                        self.device_info = device
                        logger.debug(f"device_info: {self.device_info}")
                        return device
            except Exception as wdmException:
                logger.warning(f"wdmException: {wdmException}")

            logger.info('Device does not exist, creating')

        resp = self.teams._session.post(f"{self.device_url}/devices", json=DEVICE_DATA)
        if resp is None:
            raise Exception("could not create WDM device")
        self.device_info = resp
        logger.debug(f"self.device_info: {self.device_info}")
        return resp


    def stop(self):
      def terminate():
          raise SystemExit()

      asyncio.get_event_loop().create_task(terminate())


    def run(self):
        if self.device_info is None:
            if self._get_device_info() is None:
                logger.error('could not get/create device info')
                raise Exception("No WDM device info")

        async def _websocket_recv():
            message = await self.websocket.recv()
            logger.debug("WebSocket Received Message(raw): %s\n" % message)
            try:
                msg = json.loads(message)
                loop = asyncio.get_event_loop()
                loop.run_in_executor(None, self._process_incoming_websocket_message, msg)
            except Exception as messageProcessingException:
                logger.warning(
                    f"An exception occurred while processing message. Ignoring. {messageProcessingException}")

        @backoff.on_exception(backoff.expo, websockets.ConnectionClosedError)
        @backoff.on_exception(backoff.expo, websockets.ConnectionClosedOK)
        @backoff.on_exception(backoff.expo, websockets.ConnectionClosed)
        @backoff.on_exception(backoff.expo, socket.gaierror)
        async def _connect_and_listen():
            ws_url = self.device_info['webSocketUrl']
            logger.info(f"Opening websocket connection to {ws_url}")
            async with websockets.connect(ws_url, ssl=ssl_context) as _websocket:
                self.websocket = _websocket
                logger.info("WebSocket Opened.")
                msg = {'id': str(uuid.uuid4()),
                       'type': 'authorization',
                       'data': {'token': 'Bearer ' + self.access_token}}
                await self.websocket.send(json.dumps(msg))

                while True:
                    await _websocket_recv()

        try:
            asyncio.get_event_loop().run_until_complete(_connect_and_listen())
        except Exception as runException:
            logger.error(f"runException: {runException}")
            if self._get_device_info(check_existing=False) is None:
                logger.error('could not create device info')
                raise Exception("No WDM device info")
            # trigger re-connect
            asyncio.get_event_loop().run_until_complete(_connect_and_listen())
