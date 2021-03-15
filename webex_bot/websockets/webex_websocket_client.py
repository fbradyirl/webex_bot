import asyncio
import json
import logging
import uuid

import websockets
from webexteamssdk import WebexTeamsAPI

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

    def _process_incoming_websocket_message(self, msg):
        """
        Handle websocket data.
        :param msg: The raw websocket message
        """
        if msg['data']['eventType'] == 'conversation.activity':
            activity = msg['data']['activity']
            if activity['verb'] == 'post':
                logging.debug(f"activity verb is: {activity['verb']} message id is {activity['id']}")
                # logging.debug(f"activity: {activity}")
                webex_message = self.teams.messages.get(activity['id'])

                logging.info(f"Message from {webex_message.personEmail} {webex_message.text}")
                logging.debug(f"webex_message: {webex_message}")
                if self.on_message:
                    self.on_message(webex_message, activity)
            else:
                logging.debug(f"activity verb is: {activity['verb']} ")

    def _get_device_info(self):
        """
        Get device info.

        If it doesn't exist, one will be created.
        """
        logging.debug('getting device list')
        try:
            resp = self.teams._session.get(f"{self.device_url}/devices")
            for device in resp['devices']:
                if device['name'] == DEVICE_DATA['name']:
                    self.device_info = device
                    return device
        except Exception as wdmException:
            logging.warning(f"wdmException: {wdmException}")
            pass

        logging.info('device does not exist, creating')

        resp = self.teams._session.post(f"{self.device_url}/devices", json=DEVICE_DATA)
        if resp is None:
            raise Exception("could not create WDM device")
        self.device_info = resp
        return resp

    def run(self):
        if self.device_info is None:
            if self._get_device_info() is None:
                logging.error('could not get/create device info')
                raise Exception("No WDM device info")

        async def _run():
            ws_url = self.device_info['webSocketUrl']
            logging.info(f"Opening websocket connection to {ws_url}")
            async with websockets.connect(ws_url) as websocket:
                logging.info("WebSocket Opened")
                msg = {'id': str(uuid.uuid4()),
                       'type': 'authorization',
                       'data': {
                           'token': 'Bearer ' + self.access_token
                       }
                       }
                await websocket.send(json.dumps(msg))

                while True:
                    message = await websocket.recv()
                    logging.debug("WebSocket Received Message(raw): %s\n" % message)
                    try:
                        msg = json.loads(message)
                        loop = asyncio.get_event_loop()
                        loop.run_in_executor(None, self._process_incoming_websocket_message, msg)
                    except Exception as messageProcessingException:
                        logging.warning(
                            f"An exception occurred while processing message. Ignoring. {messageProcessingException}")

        try:
            asyncio.get_event_loop().run_until_complete(_run())
        except Exception as runException:
            logging.error(f"runException: {runException}")
            # trigger re-connect
            asyncio.get_event_loop().run_until_complete(_run())
