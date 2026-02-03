import asyncio
import pytest

from webex_bot.websockets.webex_websocket_client import (
    WebexWebsocketClient,
    BACKOFF_EXCEPTIONS,
    InvalidStatus,
    _get_running_loop_or_none,
)


def _make_client():
    client = WebexWebsocketClient.__new__(WebexWebsocketClient)
    client._get_headers = lambda: {"Authorization": "Bearer test"}
    client._loop = None
    client._stop_event = None
    client.websocket = None
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


def test_get_running_loop_or_none_returns_none_when_no_loop():
    """
    _get_running_loop_or_none should return None when there's no running event loop.
    """
    result = _get_running_loop_or_none()
    assert result is None


def test_get_running_loop_or_none_returns_loop_when_running():
    """
    _get_running_loop_or_none should return the running loop when inside an async context.
    """
    async def check_loop():
        result = _get_running_loop_or_none()
        assert result is not None
        assert result == asyncio.get_running_loop()

    asyncio.run(check_loop())


def test_run_raises_error_when_loop_already_running():
    """
    run() should raise RuntimeError with helpful message when an event loop is already running.
    """
    client = _make_client()

    async def test_in_async_context():
        with pytest.raises(RuntimeError) as exc_info:
            client.run()
        assert "event loop is already running" in str(exc_info.value)
        assert "run_async()" in str(exc_info.value)

    asyncio.run(test_in_async_context())


def test_stop_sets_stop_event():
    """
    stop() should set the stop event when it exists.
    """
    client = _make_client()
    client._stop_event = asyncio.Event()
    assert not client._stop_event.is_set()
    client.stop()
    assert client._stop_event.is_set()


def test_stop_async_sets_stop_event():
    """
    stop_async() should set the stop event.
    """
    async def check_stop_async():
        client = _make_client()
        client._stop_event = asyncio.Event()
        assert not client._stop_event.is_set()
        await client.stop_async()
        assert client._stop_event.is_set()

    asyncio.run(check_stop_async())


def test_client_initializes_loop_and_stop_event_as_none():
    """
    Client should initialize _loop and _stop_event as None.
    """
    client = _make_client()
    assert client._loop is None
    assert client._stop_event is None
