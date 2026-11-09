import time
from collections.abc import Iterator
from datetime import date
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, call, patch

import pytest
from matrix import Room
from nio import RoomMemberEvent, RoomMessageText

from bot.extensions.dashboard import dashboard_extension
from bot.extensions.dashboard.dashboard_extension import (
    DAILY_SOURCES,
    TRIM_SPAN,
    _is_leave,
    _latency_ms,
    _record_command,
    _record_member_flow,
    _record_message,
    _record_reaction,
    _report_counts,
    _room_name,
    _trim_daily_charts,
)

TODAY = "2026-11-08"


@pytest.fixture
def emit() -> Iterator[MagicMock]:
    with patch.object(dashboard_extension.dachshund, "emit") as mock:
        yield mock


@pytest.fixture(autouse=True)
def today() -> Iterator[None]:
    with patch.object(dashboard_extension, "_today", return_value=TODAY):
        yield


def _room(join_rule: str = "public", users: tuple[str, ...] = ()) -> Room:
    room = SimpleNamespace(
        join_rule=join_rule,
        display_name="General",
        users=dict.fromkeys(users),
    )
    return cast(Room, room)


def _member_event(membership: str, prev_membership: str) -> RoomMemberEvent:
    event = SimpleNamespace(membership=membership, prev_membership=prev_membership)
    return cast(RoomMemberEvent, event)


def test_room_name_shows_public_rooms() -> None:
    assert _room_name(_room("public")) == "General"


@pytest.mark.parametrize("join_rule", ["invite", "knock", "restricted"])
def test_room_name_hides_non_public_rooms(join_rule: str) -> None:
    assert _room_name(_room(join_rule)) == "private"


def test_latency_ms_is_time_since_server_timestamp() -> None:
    sent = int(time.time() * 1000) - 250
    assert 250 <= _latency_ms(sent) < 1000


def test_latency_ms_never_negative() -> None:
    assert _latency_ms(int(time.time() * 1000) + 10_000) == 0


@pytest.mark.parametrize(
    ("membership", "prev_membership", "expected"),
    [("leave", "join", True), ("leave", "invite", False), ("join", "leave", False)],
)
def test_is_leave_only_for_joined_members(
    membership: str, prev_membership: str, expected: bool
) -> None:
    assert _is_leave(_member_event(membership, prev_membership)) is expected


def test_trim_daily_charts_deletes_dates_past_window(emit: MagicMock) -> None:
    _trim_daily_charts(date(2026, 11, 8))

    deleted = {c.kwargs["date"] for c in emit.mock_calls}

    assert emit.call_count == TRIM_SPAN * len(DAILY_SOURCES)
    assert "2026-10-09" not in deleted  # 30 days ago, still shown
    assert {"2026-10-08", "2026-10-02"} <= deleted
    assert "2026-10-01" not in deleted


def test_report_counts_counts_distinct_members(emit: MagicMock) -> None:
    rooms = [_room(users=("@a:x", "@b:x")), _room(users=("@b:x", "@c:x"))]
    bot = SimpleNamespace(get_rooms=lambda: rooms)

    with patch.object(dashboard_extension.extension, "_bot", bot):
        _report_counts()

    emit.assert_has_calls([call("room_count", value=2), call("member_count", value=3)])


def test_record_message_emits_latency_and_message(emit: MagicMock) -> None:
    event: Any = SimpleNamespace(
        sender="@a:x", server_timestamp=int(time.time() * 1000)
    )

    _record_message(_room("invite"), cast(RoomMessageText, event))

    assert emit.mock_calls[0].args == ("latency",)
    assert emit.mock_calls[1].args == ("average_latency",)
    emit.assert_called_with(
        "message", date=TODAY, author="@a:x", room="private", value=1
    )


def test_record_reaction_emits_day_and_emoji(emit: MagicMock) -> None:
    _record_reaction("🔥")

    emit.assert_has_calls(
        [
            call("reactions_per_day", date=TODAY, value=1),
            call("reaction_emojis", emoji="🔥", value=1),
        ]
    )


def test_record_member_flow_refreshes_counts(emit: MagicMock) -> None:
    with patch.object(dashboard_extension, "_report_counts") as report:
        _record_member_flow(joined=0, left=1)

    emit.assert_called_once_with("member_flow", joined=0, left=1)
    report.assert_called_once()


def test_record_command_emits_name_and_day(emit: MagicMock) -> None:
    _record_command("ping")

    emit.assert_has_calls(
        [
            call("on_command", name="ping", value=1),
            call("commands_per_day", date=TODAY, value=1),
        ]
    )
