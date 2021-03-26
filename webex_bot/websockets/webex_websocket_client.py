import asyncio
import json
import logging
import socket
import uuid

import backoff
import websockets
from webexteamssdk import WebexTeamsAPI

DEFAULT_DEVICE_URL = "https://wdm-a.wbx2.com/wdm/api/v1"

DEVICE_DATA = {
    "deviceName": "webex_bot_pypi-client",
    "deviceType": "DESKTOP",
    "localizedModel": "webex-bot-pypi",
    "model": "webex_bot_pypi",
    "name": "webex_bot_pypi-client",
    "systemName": "webex_bot_pypi",
    "systemVersion": "0.1"
}


class WebexWebsocketClient(object):
    def __init__(self,
                 access_token,
                 device_url=DEFAULT_DEVICE_URL,
                 on_message=None):
        self.access_token = access_token
        self.teams = WebexTeamsAPI(access_token=access_token)
        self.device_url = device_url
        self.device_info = None
        self.on_message = on_message
        self.websocket = None

    def _process_incoming_websocket_message(self, msg):
        """
        Handle websocket data.
        :param msg: The raw websocket message
        """
        if msg['data']['eventType'] == 'conversation.activity':
            activity = msg['data']['activity']
            if activity['verb'] == 'post':
                message_id = activity['id']
                logging.debug(f"activity verb=post. message id={message_id}")
                webex_message = self.teams.messages.get(activity['id'])
                logging.debug(f"webex_message: {webex_message}")
                if self.on_message:
                    # ack message first
                    self._ack_message(message_id)
                    # Now process it with the handler
                    self.on_message(webex_message, activity)
            else:
                logging.debug(f"activity verb is: {activity['verb']} ")

    def _ack_message(self, message_id):
        """
        Ack that this message has been processed. This will prevent the
        message coming again.
        @param message_id: activity message 'id'
        """
        logging.debug(f"WebSocket ack message with id={message_id}")
        ack_message = {'type': 'ack',
                       'messageId': message_id}
        self.websocket.send(json.dumps(ack_message))
        logging.debug(f"WebSocket ack message with id={message_id}. Complete.")

    def _get_device_info(self):
        """
        Get device info from Webex Cloud.

        If it doesn't exist, one will be created.
        """
        logging.debug('Getting device list')
        try:
            resp = self.teams._session.get(f"{self.device_url}/devices")
            for device in resp['devices']:
                if device['name'] == DEVICE_DATA['name']:
                    self.device_info = device
                    logging.debug(f"device_info: {self.device_info}")
                    return device
        except Exception as wdmException:
            logging.warning(f"wdmException: {wdmException}")

        logging.info('Device does not exist, creating')

        resp = self.teams._session.post(f"{self.device_url}/devices", json=DEVICE_DATA)
        if resp is None:
            raise Exception("could not create WDM device")
        self.device_info = resp
        logging.debug(f"self.device_info: {self.device_info}")
        return resp

    def run(self):
        if self.device_info is None:
            if self._get_device_info() is None:
                logging.error('could not get/create device info')
                raise Exception("No WDM device info")

        async def _websocket_recv():
            message = await self.websocket.recv()
            logging.debug("WebSocket Received Message(raw): %s\n" % message)
            try:
                msg = json.loads(message)
                loop = asyncio.get_event_loop()
                loop.run_in_executor(None, self._process_incoming_websocket_message, msg)
            except Exception as messageProcessingException:
                logging.warning(
                    f"An exception occurred while processing message. Ignoring. {messageProcessingException}")

        @backoff.on_exception(backoff.expo, websockets.exceptions.ConnectionClosedError)
        @backoff.on_exception(backoff.expo, socket.gaierror)
        async def _connect_and_listen():
            ws_url = self.device_info['webSocketUrl']
            logging.info(f"Opening websocket connection to {ws_url}")
            async with websockets.connect(ws_url) as _websocket:
                self.websocket = _websocket
                logging.info(f"WebSocket Opened.")
                msg = {'id': str(uuid.uuid4()),
                       'type': 'authorization',
                       'data': {'token': 'Bearer ' + self.access_token}}
                await self.websocket.send(json.dumps(msg))

                while True:
                    await _websocket_recv()

        try:
            asyncio.get_event_loop().run_until_complete(_connect_and_listen())
        except Exception as runException:
            logging.error(f"runException: {runException}")
            # trigger re-connect
            asyncio.get_event_loop().run_until_complete(_connect_and_listen())
