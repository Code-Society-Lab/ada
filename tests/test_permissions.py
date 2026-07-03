import pytest
from types import SimpleNamespace

from bot.permissions import is_moderator


def make_ctx(sender: str, sender_level: int, required_level: int = 50):
    power_levels = SimpleNamespace(
        defaults=SimpleNamespace(kick=required_level),
        get_user_level=lambda user_id: sender_level,
    )

    room = SimpleNamespace(
        matrix_room=SimpleNamespace(
            power_levels=power_levels,
        )
    )

    return SimpleNamespace(sender=sender, room=room)


@pytest.mark.asyncio
async def test_is_moderator_accepts_user_at_required_power_level() -> None:
    ctx = make_ctx("@mod:example.com", sender_level=50)

    assert await is_moderator(ctx) is True  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_is_moderator_accepts_user_above_required_power_level() -> None:
    ctx = make_ctx("@admin:example.com", sender_level=100)

    assert await is_moderator(ctx) is True  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_is_moderator_rejects_user_below_required_power_level() -> None:
    ctx = make_ctx("@user:example.com", sender_level=0)

    assert await is_moderator(ctx) is False  # type: ignore[arg-type]
