from types import SimpleNamespace

from bot.extensions.welcome_extension import _is_new_join, _member_display_name


class _RoomWithName:
    def user_name(self, user_id: str) -> str:
        return f"user:{user_id}"


class _RoomError:
    def user_name(self, user_id: str) -> str:
        raise RuntimeError("boom")


def test_is_new_join_true_for_join_transition() -> None:
    event = SimpleNamespace(membership="join", prev_membership="invite")
    assert _is_new_join(event) is True


def test_is_new_join_false_when_already_joined() -> None:
    event = SimpleNamespace(membership="join", prev_membership="join")
    assert _is_new_join(event) is False


def test_member_display_name_uses_room_name() -> None:
    assert _member_display_name(_RoomWithName(), "@u:example.org") == "user:@u:example.org"


def test_member_display_name_falls_back_to_user_id() -> None:
    assert _member_display_name(_RoomError(), "@u:example.org") == "@u:example.org"
