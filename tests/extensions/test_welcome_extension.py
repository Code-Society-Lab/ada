import pytest
from types import SimpleNamespace

from bot.extensions.welcome_extension import _is_new_join, _member_display_name, _welcome


class _RoomWithName:
    def __init__(self):
        self.sent = []

    def user_name(self, user_id: str) -> str:
        return f"user:{user_id}"

    async def send(self, message: str) -> None:
        self.sent.append(message)


class _RoomNoName:
    def __init__(self):
        self.sent = []

    def user_name(self, user_id: str) -> None:
        return None

    async def send(self, message: str) -> None:
        self.sent.append(message)


def test_is_new_join_true_for_join_transition() -> None:
    event = SimpleNamespace(membership="join", prev_membership="invite")
    assert _is_new_join(event) is True


def test_is_new_join_false_when_already_joined() -> None:
    event = SimpleNamespace(membership="join", prev_membership="join")
    assert _is_new_join(event) is False


def test_member_display_name_uses_room_name() -> None:
    assert _member_display_name(_RoomWithName(), "@u:example.org") == "user:@u:example.org"


def test_member_display_name_falls_back_to_user_id() -> None:
    assert _member_display_name(_RoomNoName(), "@u:example.org") == "@u:example.org"


@pytest.mark.asyncio
async def test_welcome_uses_display_name() -> None:
    room = _RoomWithName()
    await _welcome(room, "@u:example.org")
    assert room.sent == ["Welcome user:@u:example.org! Glad to have you here."]


@pytest.mark.asyncio
async def test_welcome_falls_back_to_user_id() -> None:
    room = _RoomNoName()
    await _welcome(room, "@u:example.org")
    assert room.sent == ["Welcome @u:example.org! Glad to have you here."]
