import pytest
from matrix.errors import MatrixError
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

from bot.extensions.moderation.kick_service import kick_from_context
from matrix import Context


@pytest.mark.asyncio
async def test_kick_from_context__with_no_parent_space__expect_current_room_kicked() -> (
    None
):
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
async def test_kick_from_context__with_current_room_matrix_error__expect_current_room_recorded_failed() -> (
    None
):
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
async def test_kick_from_context__with_parent_space_targets__expect_successes_and_failures_recorded() -> (
    None
):
    space = SimpleNamespace(room_id="!space:example.com", kick_user=AsyncMock())
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
    ctx = SimpleNamespace(
        room=SimpleNamespace(room_id="!current:example.com"),
        bot=bot,
    )

    async def collect_room_ids(_ctx, _space):
        return [
            "!success:example.com",
            "!failed:example.com",
            "!missing:example.com",
        ]

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
    space.kick_user.assert_awaited_once_with("@target:example.com", reason="spam")
    assert result.kicked_room_ids == ["!success:example.com", "!space:example.com"]
    assert result.failed_room_ids == ["!failed:example.com", "!missing:example.com"]


@pytest.mark.asyncio
async def test_kick_from_context__with_nested_space_children__expect_nested_targets_and_parent_space_kicked() -> (
    None
):
    root_space = SimpleNamespace(
        room_id="!root-space:example.com",
        room_type="m.space",
        children=["!nested-space:example.com"],
        kick_user=AsyncMock(),
    )
    nested_space = SimpleNamespace(
        room_id="!nested-space:example.com",
        room_type="m.space",
        children=["!leaf-room:example.com"],
        kick_user=AsyncMock(),
    )
    leaf_room = SimpleNamespace(
        room_id="!leaf-room:example.com",
        room_type=None,
        children=[],
        kick_user=AsyncMock(),
    )

    bot = MagicMock()
    bot.get_room.side_effect = lambda room_id: {
        "!root-space:example.com": root_space,
        "!nested-space:example.com": nested_space,
        "!leaf-room:example.com": leaf_room,
    }[room_id]
    ctx = SimpleNamespace(
        room=SimpleNamespace(room_id="!current:example.com"),
        bot=bot,
    )

    with patch(
        "bot.extensions.moderation.kick_service.get_parent_space_id",
        return_value="!root-space:example.com",
    ):
        result = await kick_from_context(
            cast(Context, ctx), "@target:example.com", "spam"
        )

    nested_space.kick_user.assert_awaited_once_with(
        "@target:example.com", reason="spam"
    )
    leaf_room.kick_user.assert_awaited_once_with("@target:example.com", reason="spam")
    root_space.kick_user.assert_awaited_once_with("@target:example.com", reason="spam")
    assert result.kicked_room_ids == [
        "!nested-space:example.com",
        "!leaf-room:example.com",
        "!root-space:example.com",
    ]
    assert result.failed_room_ids == []
