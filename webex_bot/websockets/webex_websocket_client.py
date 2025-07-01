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
from webexpythonsdk import WebexAPI
from websockets.exceptions import InvalidStatusCode

from webex_bot import __version__

try:
    from websockets_proxy import Proxy, proxy_connect
except ImportError:
    Proxy = None
    proxy_connect = None

logger = logging.getLogger(__name__)

DEFAULT_U2C_URL = "https://u2c.wbx2.com/u2c/api/v1/catalog"

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

MAX_BACKOFF_TIME = 240


class WebexWebsocketClient(object):
    def __init__(self,
                 access_token,
                 on_message=None,
                 on_card_action=None,
                 proxies=None):
        self.access_token = access_token
        self.teams = WebexAPI(access_token=access_token, proxies=proxies)
        self.tracking_id = f"webex-bot_{uuid.uuid4()}"
        self.session = requests.Session()
        self.session.headers = self._get_headers()
        sdk_ua = self.teams._session.headers["User-Agent"]
        self.teams._session.update_headers(self._get_headers(add_to_ua=f" ({sdk_ua})"))
        # log the tracking ID
        logger.info(f"Tracking ID: {self.tracking_id}")
        self.device_info = None
        self.device_url = self._get_device_url()
        self.on_message = on_message
        self.on_card_action = on_card_action
        self.proxies = proxies
        self.websocket = None
        self.share_id = None
        if self.proxies:
            self.session.proxies = proxies
        if self.proxies:
            # Connecting through a proxy
            if proxy_connect is None:
                raise ImportError("Failed to load libraries for proxy, maybe forgot [proxy] option during installation.")

    def _get_headers(self, add_to_ua=''):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-type": "application/json;charset=utf-8",
            "User-Agent": f"webex_bot/{__version__}{add_to_ua}",
            "trackingid": self.tracking_id
        }

    def _process_incoming_websocket_message(self, msg):
        """
        Handle websocket data.
        :param msg: The raw websocket message
        """
        logger.info(f"msg['data'] = {msg['data']}")
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
            elif activity['verb'] == 'share':
                logger.debug(f"activity={activity}")
                self.share_id = activity['id']
                return
            elif activity['verb'] == 'update':
                logger.debug(f"activity={activity}")

                object = activity['object']
                if object['objectType'] == 'content' and object['contentCategory'] == 'documents':
                    if 'files' in object.keys():
                        for item in object['files']['items']:
                            if not item['malwareQuarantineState'] == 'safe':
                                return
                    else:
                        return
                else:
                    return
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
        logger.debug(f"activity verb={activity['verb']}. message id={activity_id}")
        conversation_url = activity['target']['url']
        conv_target_id = activity['target']['id']
        verb = "messages" if activity['verb'] in ["post", "update"] else "attachment/actions"
        if activity['verb'] == "update" and self.share_id is not None:
            activity_id = self.share_id
            self.share_id = None
        logger.debug(f"activity_id={activity_id}")
        conversation_message_url = conversation_url.replace(f"conversations/{conv_target_id}",
                                                            f"{verb}/{activity_id}")
        conversation_message = self.session.get(conversation_message_url).json()
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

    def _get_device_url(self):
        params = {"format": "hostmap"}
        response = self.session.get(DEFAULT_U2C_URL, params=params)

        # check for 401 Unauthorized
        if response.status_code == 401:
            logger.error("Unauthorized access. Please check your access token.")
            raise Exception("Unauthorized access. Please check your access token.")

        data = response.json()

        wdm_url = data["serviceLinks"].get("wdm")  # or whatever key your hostmap uses
        logging.info(f"wdm url: {wdm_url}")
        return wdm_url


    def _get_device_info(self, check_existing=True):
        """
        Get device info from Webex Cloud.

        If it doesn't exist, one will be created.
        """
        if check_existing:
            logger.debug('Getting device list')
            try:
                resp = self.session.get(f"{self.device_url}/devices")
                for device in resp.json()['devices']:
                    if device['name'] == DEVICE_DATA['name']:
                        self.device_info = device
                        logger.debug(f"device_info: {self.device_info}")
                        return device
            except Exception as wdmException:
                logger.warning(f"wdmException: {wdmException}")

            logger.info('Device does not exist, creating')

        resp = self.session.post(f"{self.device_url}/devices", json=DEVICE_DATA)
        if resp is None:
            raise Exception("could not create WDM device")
        self.device_info = resp.json()
        logger.debug(f"self.device_info: {self.device_info}")
        return self.device_info

    def stop(self):
        def terminate():
            raise SystemExit()

        asyncio.get_event_loop().create_task(terminate())

    def run(self):
        if self.device_info is None:
            if self._get_device_info() is None:
                logger.error('could not get/create device info')
                raise Exception("No WDM device info")

        # Pull out URL now so we can log it on failure
        ws_url = self.device_info.get('webSocketUrl')

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

        @backoff.on_exception(
            backoff.expo,
            (
                websockets.ConnectionClosedError,
                websockets.ConnectionClosedOK,
                websockets.ConnectionClosed,
                socket.gaierror,
                InvalidStatusCode,
            ),
            max_time=MAX_BACKOFF_TIME
        )
        async def _connect_and_listen():
            ws_url = self.device_info['webSocketUrl']
            logger.info(f"Opening websocket connection to {ws_url}")

            if self.proxies and "wss" in self.proxies:
                logger.info(f"Using proxy for websocket connection: {self.proxies['wss']}")
                proxy = Proxy.from_url(self.proxies["wss"])
                connect = proxy_connect(ws_url, ssl=ssl_context, proxy=proxy, extra_headers=self._get_headers())
            elif self.proxies and "https" in self.proxies:
                logger.info(f"Using proxy for websocket connection: {self.proxies['https']}")
                proxy = Proxy.from_url(self.proxies["https"])
                connect = proxy_connect(ws_url, ssl=ssl_context, proxy=proxy, extra_headers=self._get_headers())
            else:
                logger.debug(f"Not using proxy for websocket connection.")
                connect = websockets.connect(ws_url, ssl=ssl_context, extra_headers=self._get_headers())

            async with connect as _websocket:
                self.websocket = _websocket
                logger.info("WebSocket Opened.")
                msg = {'id': str(uuid.uuid4()),
                       'type': 'authorization',
                       'data': {'token': 'Bearer ' + self.access_token}}
                await self.websocket.send(json.dumps(msg))

                while True:
                    await _websocket_recv()

        # Track the number of consecutive 404 errors to prevent infinite loops
        max_404_retries = 3
        current_404_retries = 0
        
        while True:
            try:
                asyncio.get_event_loop().run_until_complete(_connect_and_listen())
                # If we get here, the connection was successful, so break out of the loop
                break
            except InvalidStatusCode as e:
                logger.error(f"WebSocket handshake to {ws_url} failed with status {e.status_code}")
                
                if e.status_code == 404:
                    current_404_retries += 1
                    if current_404_retries >= max_404_retries:
                        logger.error(f"Reached maximum retries ({max_404_retries}) for 404 errors. Giving up.")
                        raise Exception(f"Unable to connect to WebSocket after {max_404_retries} attempts. Device registration may be invalid.")
                    
                    logger.info(f"Refreshing WDM device info and retrying... (Attempt {current_404_retries} of {max_404_retries})")
                    # Force a new device registration
                    self._get_device_info(check_existing=False)
                    # Update ws_url with the new device info
                    ws_url = self.device_info.get('webSocketUrl')
                    
                    # Add a delay before retrying to avoid hammering the server
                    logger.info(f"Waiting 5 seconds before retry attempt {current_404_retries}...")
                    asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))
                else:
                    # For non-404 errors, just raise the exception
                    raise
            except Exception as runException:
                logger.error(f"runException: {runException}")
                
                # Check if we can get device info
                if self._get_device_info(check_existing=False) is None:
                    logger.error('could not create device info')
                    raise Exception("No WDM device info")
                    
                # Update the URL in case it changed
                ws_url = self.device_info.get('webSocketUrl')
                
                # Wait a bit before reconnecting
                logger.info("Waiting 5 seconds before attempting to reconnect...")
                asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))
