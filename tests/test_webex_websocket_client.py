from unittest.mock import MagicMock

from webex_bot.websockets.webex_websocket_client import (
    WebexWebsocketClient,
    BACKOFF_EXCEPTIONS,
    InvalidStatus,
)


def _make_client():
    client = WebexWebsocketClient.__new__(WebexWebsocketClient)
    client._get_headers = lambda: {"Authorization": "Bearer test"}
    return client


def _make_activity(verb="post", activity_id="act-123", conv_id="conv-456",
                   conv_url="https://conv.example.com/conversations/conv-456"):
    return {
        "id": activity_id,
        "verb": verb,
        "target": {"url": conv_url, "id": conv_id},
    }


def _make_client_for_message_processing():
    """Build a client with enough stubs to test message processing paths."""
    client = _make_client()
    client.session = MagicMock()
    client.share_id = None
    client.on_message = MagicMock()
    client.on_card_action = MagicMock()
    client.teams = MagicMock()
    return client


def test_get_websocket_connect_kwargs_prefers_extra_headers():
    def connect(*, extra_headers=None):
        return extra_headers

    client = _make_client()
    assert client._get_websocket_connect_kwargs(connect) == {
        "extra_headers": {"Authorization": "Bearer test"}
    }


def test_get_websocket_connect_kwargs_uses_additional_headers():
    def connect(*, additional_headers=None):
        return additional_headers

    client = _make_client()
    assert client._get_websocket_connect_kwargs(connect) == {
        "additional_headers": {"Authorization": "Bearer test"}
    }


def test_get_websocket_connect_kwargs_fallback_to_extra_headers():
    def connect(*, headers=None):
        return headers

    client = _make_client()
    assert client._get_websocket_connect_kwargs(connect) == {
        "extra_headers": {"Authorization": "Bearer test"}
    }


def test_invalid_status_not_in_backoff_exceptions():
    """
    InvalidStatus (e.g. HTTP 404) should NOT be in BACKOFF_EXCEPTIONS.

    When the websocket connection fails with a 404, it means the device
    registration is stale. We need to immediately refresh the device info
    rather than wasting time on backoff retries with the same stale URL.
    """
    assert InvalidStatus not in BACKOFF_EXCEPTIONS, (
        "InvalidStatus should not be in BACKOFF_EXCEPTIONS. "
        "404 errors need immediate device refresh, not backoff retries."
    )


# --- _get_base64_message_id tests ---

class TestGetBase64MessageId:
    def test_returns_id_on_success(self):
        client = _make_client_for_message_processing()
        activity = _make_activity()
        response = MagicMock(ok=True)
        response.json.return_value = {"id": "base64-msg-id"}
        client.session.get.return_value = response

        result = client._get_base64_message_id(activity)
        assert result == "base64-msg-id"

    def test_returns_none_on_http_error(self):
        client = _make_client_for_message_processing()
        activity = _make_activity()
        response = MagicMock(ok=False, status_code=404)
        client.session.get.return_value = response

        result = client._get_base64_message_id(activity)
        assert result is None

    def test_returns_none_when_id_missing_from_response(self):
        client = _make_client_for_message_processing()
        activity = _make_activity()
        response = MagicMock(ok=True)
        response.json.return_value = {"message": "not found"}
        client.session.get.return_value = response

        result = client._get_base64_message_id(activity)
        assert result is None


# --- _process_incoming_websocket_message tests ---

class TestProcessIncomingWebsocketMessage:
    def _wrap_activity(self, activity):
        return {"data": {"eventType": "conversation.activity", "activity": activity}}

    def test_post_skips_when_message_id_unresolvable(self):
        client = _make_client_for_message_processing()
        client._get_base64_message_id = MagicMock(return_value=None)
        activity = _make_activity(verb="post")

        client._process_incoming_websocket_message(self._wrap_activity(activity))

        client.on_message.assert_not_called()
        client.teams.messages.get.assert_not_called()

    def test_post_processes_when_message_id_resolved(self):
        client = _make_client_for_message_processing()
        client._get_base64_message_id = MagicMock(return_value="msg-id")
        client.websocket = MagicMock()
        client._ack_message = MagicMock()
        activity = _make_activity(verb="post")

        client._process_incoming_websocket_message(self._wrap_activity(activity))

        client.teams.messages.get.assert_called_once_with("msg-id")
        client.on_message.assert_called_once()

    def test_cardaction_skips_when_message_id_unresolvable(self):
        client = _make_client_for_message_processing()
        client._get_base64_message_id = MagicMock(return_value=None)
        activity = _make_activity(verb="cardAction")

        client._process_incoming_websocket_message(self._wrap_activity(activity))

        client.on_card_action.assert_not_called()
        client.teams.attachment_actions.get.assert_not_called()

    def test_cardaction_processes_when_message_id_resolved(self):
        client = _make_client_for_message_processing()
        client._get_base64_message_id = MagicMock(return_value="action-id")
        client.websocket = MagicMock()
        client._ack_message = MagicMock()
        activity = _make_activity(verb="cardAction")

        client._process_incoming_websocket_message(self._wrap_activity(activity))

        client.teams.attachment_actions.get.assert_called_once_with("action-id")
        client.on_card_action.assert_called_once()

    def test_update_skips_when_message_id_unresolvable(self):
        client = _make_client_for_message_processing()
        client._get_base64_message_id = MagicMock(return_value=None)
        activity = _make_activity(verb="update")
        activity["object"] = {
            "objectType": "content",
            "contentCategory": "documents",
            "files": {"items": [{"malwareQuarantineState": "safe"}]},
        }

        client._process_incoming_websocket_message(self._wrap_activity(activity))

        client.on_message.assert_not_called()
        client.teams.messages.get.assert_not_called()
