import pytest
from matrix.errors import MatrixError
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

from bot.extensions.moderation.kick_service import kick_from_context
from matrix import Context


@pytest.mark.asyncio
async def test_kick_from_context_kicks_current_room_when_not_in_space() -> None:
    ctx = SimpleNamespace(
        room=SimpleNamespace(
            room_id="!room:example.com",
            kick_user=AsyncMock(),
        ),
    )

    with patch(
        "bot.extensions.moderation.kick_service.get_parent_space_id",
        return_value=None,
    ):
        result = await kick_from_context(
            cast(Context, ctx), "@target:example.com", "spam"
        )

    ctx.room.kick_user.assert_awaited_once_with("@target:example.com", reason="spam")
    assert result.kicked_room_ids == ["!room:example.com"]
    assert result.failed_room_ids == []


@pytest.mark.asyncio
async def test_kick_from_context_records_current_room_failure() -> None:
    ctx = SimpleNamespace(
        room=SimpleNamespace(
            room_id="!room:example.com",
            kick_user=AsyncMock(side_effect=MatrixError("not allowed")),
        ),
    )

    with patch(
        "bot.extensions.moderation.kick_service.get_parent_space_id",
        return_value=None,
    ):
        result = await kick_from_context(
            cast(Context, ctx), "@target:example.com", "spam"
        )

    assert result.kicked_room_ids == []
    assert result.failed_room_ids == ["!room:example.com"]


@pytest.mark.asyncio
async def test_kick_from_context_collects_space_successes_and_failures() -> None:
    space = SimpleNamespace(room_id="!space:example.com")
    successful_room = SimpleNamespace(kick_user=AsyncMock())
    failed_room = SimpleNamespace(
        kick_user=AsyncMock(side_effect=MatrixError("denied"))
    )

    bot = MagicMock()
    bot.get_room.side_effect = lambda room_id: {
        "!space:example.com": space,
        "!success:example.com": successful_room,
        "!failed:example.com": failed_room,
        "!missing:example.com": None,
    }[room_id]
    ctx = SimpleNamespace(bot=bot)

    async def collect_room_ids(_ctx, _space, room_ids, _seen):
        room_ids.extend(
            [
                "!success:example.com",
                "!failed:example.com",
                "!missing:example.com",
            ]
        )

    with (
        patch(
            "bot.extensions.moderation.kick_service.get_parent_space_id",
            return_value="!space:example.com",
        ),
        patch(
            "bot.extensions.moderation.kick_service.collect_space_child_room_ids",
            side_effect=collect_room_ids,
        ),
    ):
        result = await kick_from_context(
            cast(Context, ctx), "@target:example.com", "spam"
        )

    successful_room.kick_user.assert_awaited_once_with(
        "@target:example.com", reason="spam"
    )
    failed_room.kick_user.assert_awaited_once_with("@target:example.com", reason="spam")
    assert result.kicked_room_ids == ["!success:example.com"]
    assert result.failed_room_ids == ["!failed:example.com", "!missing:example.com"]
