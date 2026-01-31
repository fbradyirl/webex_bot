import types
import warnings

import pytest

warnings.filterwarnings(
    "ignore",
    category=PendingDeprecationWarning,
    module=r"webexpythonsdk\.environment",
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r"websockets\..*",
)

from webex_bot.webex_bot import WebexBot
from webex_bot.websockets.webex_websocket_client import WebexWebsocketClient


class DummyPerson:
    def __init__(self, display_name="Webex Bot", email="bot@example.com", avatar="https://example.com/avatar.png"):
        self.displayName = display_name
        self.emails = [email]
        self.avatar = avatar
        self.type = "bot"


class DummyPeople:
    def __init__(self, me_person):
        self._me_person = me_person

    def me(self):
        return self._me_person


class DummyMessages:
    def __init__(self):
        self.created = []
        self.deleted = []

    def create(self, **kwargs):
        self.created.append(kwargs)
        return types.SimpleNamespace(id="message-1")

    def delete(self, message_id):
        self.deleted.append(message_id)


class DummyMemberships:
    def __init__(self, member_emails=None):
        self.member_emails = set(member_emails or [])

    def list(self, roomId, personEmail):
        if personEmail in self.member_emails:
            return [types.SimpleNamespace(personEmail=personEmail)]
        return []


class DummyTeams:
    def __init__(self, person_email="bot@example.com", member_emails=None):
        self.people = DummyPeople(DummyPerson(email=person_email))
        self.messages = DummyMessages()
        self.memberships = DummyMemberships(member_emails=member_emails)


@pytest.fixture
def teams_api():
    return DummyTeams(member_emails={"member@example.com"})


@pytest.fixture
def bot(monkeypatch, teams_api):
    def fake_init(self, access_token, bot_name, on_message=None, on_card_action=None, proxies=None):
        self.access_token = access_token
        self.teams = teams_api
        self.on_message = on_message
        self.on_card_action = on_card_action
        self.proxies = proxies
        self.websocket = None

    monkeypatch.setattr(WebexWebsocketClient, "__init__", fake_init)
    return WebexBot(teams_bot_token="test-token", include_demo_commands=False)


def make_activity(actor_type="PERSON", actor_email="user@example.com", tags=None, parent=None, activity_id="act-1"):
    if tags is None:
        tags = ["ONE_ON_ONE"]
    activity = {
        "id": activity_id,
        "actor": {"type": actor_type, "emailAddress": actor_email},
        "target": {"tags": tags},
    }
    if parent is not None:
        activity["parent"] = parent
    return activity


@pytest.fixture
def one_on_one_activity():
    return make_activity()


@pytest.fixture
def group_activity():
    return make_activity(tags=["GROUP"])


@pytest.fixture
def teams_message():
    return types.SimpleNamespace(
        roomId="room-1",
        text="help",
        personEmail="user@example.com",
        messageId="msg-1",
    )
