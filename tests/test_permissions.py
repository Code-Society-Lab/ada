import pytest
from types import SimpleNamespace

from bot.permissions import is_moderator


@pytest.mark.asyncio
async def test_is_moderator_accepts_configured_list() -> None:
    config = SimpleNamespace(
        get=lambda _key, section, default: [
            "@admin:example.com",
            "@mod:example.com",
        ]
    )
    ctx = SimpleNamespace(bot=SimpleNamespace(config=config), sender="@mod:example.com")

    assert await is_moderator(ctx) is True  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_is_moderator_accepts_comma_separated_config_string() -> None:
    config = SimpleNamespace(
        get=lambda _key, section, default: ("@admin:example.com, @mod:example.com, ")
    )
    ctx = SimpleNamespace(bot=SimpleNamespace(config=config), sender="@mod:example.com")

    assert await is_moderator(ctx) is True  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_is_moderator_rejects_unconfigured_user() -> None:
    config = SimpleNamespace(get=lambda _key, section, default: ["@admin:example.com"])
    ctx = SimpleNamespace(
        bot=SimpleNamespace(config=config), sender="@user:example.com"
    )

    assert await is_moderator(ctx) is False  # type: ignore[arg-type]
