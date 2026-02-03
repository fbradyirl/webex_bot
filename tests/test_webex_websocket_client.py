from webex_bot.websockets.webex_websocket_client import (
    WebexWebsocketClient,
    BACKOFF_EXCEPTIONS,
    InvalidStatus,
)


def _make_client():
    client = WebexWebsocketClient.__new__(WebexWebsocketClient)
    client._get_headers = lambda: {"Authorization": "Bearer test"}
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
