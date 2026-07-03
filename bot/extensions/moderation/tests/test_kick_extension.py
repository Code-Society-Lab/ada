import pytest
from matrix.errors import MatrixError
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

from matrix import Context, Room, Space
from bot.extensions.moderation.kick_service import kick_from_context, kick_from_rooms


def as_async_mock(value: Any) -> AsyncMock:
    return cast(AsyncMock, value)


def as_mock(value: Any) -> MagicMock:
    return cast(MagicMock, value)


def mock_room(
    room_id: str,
    *,
    kick_error: Exception | None = None,
) -> Room:
    room = MagicMock(spec=Room)
    room.room_id = room_id
    room.name = room_id

    if kick_error:
        cast(Any, room).get_members = AsyncMock(return_value=["@target:example.com"])
    else:
        cast(Any, room).get_members = AsyncMock(
            side_effect=[
                ["@target:example.com"],
                [],
            ]
        )

    cast(Any, room).kick_user = AsyncMock(side_effect=kick_error)

    return cast(Room, room)


def mock_space(room_id: str, children: list[Room | Space]) -> Space:
    space = MagicMock(spec=Space)
    space.room_id = room_id
    space.name = room_id
    cast(Any, space).get_children = MagicMock(return_value=children)
    cast(Any, space).kick_user = AsyncMock()
    return cast(Space, space)


@pytest.mark.asyncio
async def test_kick_from_rooms__skips_when_user_is_not_member() -> None:
    room = mock_room("!room:example.com")
    cast(Any, room).get_members = AsyncMock(return_value=[])

    result = await kick_from_rooms(
        "@target:example.com",
        [room],
        reason="spam",
    )

    as_async_mock(room.kick_user).assert_not_awaited()
    assert result.kicked_room_ids == []
    assert result.failed_room_ids == []


@pytest.mark.asyncio
async def test_kick_from_rooms__records_successes_failures_and_dedupes() -> None:
    successful_room = mock_room("!success:example.com")
    failed_room = mock_room(
        "!failed:example.com",
        kick_error=MatrixError("denied"),
    )

    result = await kick_from_rooms(
        "@target:example.com",
        [successful_room, failed_room, successful_room],
        reason="spam",
    )

    as_async_mock(successful_room.kick_user).assert_awaited_once_with(
        "@target:example.com", reason="spam"
    )
    as_async_mock(failed_room.kick_user).assert_awaited_once_with(
        "@target:example.com", reason="spam"
    )

    assert result.target_user_id == "@target:example.com"
    assert result.reason == "spam"
    assert result.space_id is None
    assert result.kicked_room_ids == ["!success:example.com"]
    assert result.failed_room_ids == ["!failed:example.com"]


@pytest.mark.asyncio
async def test_kick_from_rooms__includes_space_id_when_space_provided() -> None:
    room = mock_room("!room:example.com")
    space = mock_space("!space:example.com", [])

    result = await kick_from_rooms(
        "@target:example.com",
        [room],
        reason="spam",
        space=space,
    )

    assert result.space_id == "!space:example.com"
    assert result.kicked_room_ids == ["!room:example.com"]
    assert result.failed_room_ids == []


@pytest.mark.asyncio
async def test_kick_from_context__without_parent_space__kicks_current_room() -> None:
    current_room = mock_room("!current:example.com")
    ctx = SimpleNamespace(room=current_room)

    with patch(
        "bot.extensions.moderation.kick_service.get_parent_space",
        return_value=None,
    ):
        result = await kick_from_context(
            cast(Context, ctx),
            "@target:example.com",
            "spam",
        )

    as_async_mock(current_room.kick_user).assert_awaited_once_with(
        "@target:example.com", reason="spam"
    )
    assert result.kicked_room_ids == ["!current:example.com"]
    assert result.failed_room_ids == []


@pytest.mark.asyncio
async def test_kick_from_context__with_parent_space__kicks_room_children_only() -> None:
    child_room = mock_room("!child-room:example.com")
    child_space = mock_space("!child-space:example.com", [])
    parent_space = mock_space(
        "!parent-space:example.com",
        [child_room, child_space],
    )
    ctx = SimpleNamespace(room=mock_room("!current:example.com"))

    with patch(
        "bot.extensions.moderation.kick_service.get_parent_space",
        return_value=parent_space,
    ):
        result = await kick_from_context(
            cast(Context, ctx),
            "@target:example.com",
            "spam",
        )

    as_mock(parent_space.get_children).assert_called_once_with(depth=3)
    as_async_mock(child_room.kick_user).assert_awaited_once_with(
        "@target:example.com", reason="spam"
    )
    as_async_mock(child_space.kick_user).assert_not_awaited()

    assert result.space_id == "!parent-space:example.com"
    assert result.kicked_room_ids == ["!child-room:example.com"]
    assert result.failed_room_ids == []
