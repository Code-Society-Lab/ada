import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bot.extensions.messages import search_extension


def test_extract_search_terms__with_valid_queries__expect_terms_list():
    queries = ("content=hello", "sender=@user:matrix.org")
    result = list(search_extension._extract_search_terms(queries))

    assert result == [
        ("content", "hello"),
        ("sender", "@user:matrix.org"),
    ]


def test_extract_search_terms__with_missing_equals__expect_value_error():
    queries = ("invalid_query",)

    with pytest.raises(ValueError):
        list(search_extension._extract_search_terms(queries))


def test_extract_search_terms__with_empty_value__expect_value_error():
    queries = ("content=", "sender=user")

    with pytest.raises(ValueError, match="Empty value for field"):
        list(search_extension._extract_search_terms(queries))


@pytest.mark.asyncio
async def test_on_message__with_command_prefix__expect_is_command_true():
    room = MagicMock()

    event = MagicMock()
    event.body = "!search hello"
    event.server_timestamp = "123"
    event.sender = "@user:matrix.org"
    event.event_id = "evt1"

    with (
        patch.object(
            search_extension.extension,
            "_bot",
            MagicMock(prefix="!"),
        ),
        patch("bot.extensions.messages.search_extension.Message.create") as mock_create,
    ):
        await search_extension.on_message(room, event)

        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        assert kwargs["is_command"] is True


@pytest.mark.asyncio
async def test_on_message__with_regular_message__expect_is_command_false():
    room = MagicMock()

    event = MagicMock()
    event.body = "hello"
    event.server_timestamp = "123"
    event.sender = "@user:matrix.org"
    event.event_id = "evt1"

    with (
        patch.object(
            search_extension.extension,
            "_bot",
            MagicMock(prefix="!"),
        ),
        patch("bot.extensions.messages.search_extension.Message.create") as mock_create,
    ):
        await search_extension.on_message(room, event)

        kwargs = mock_create.call_args.kwargs
        assert kwargs["is_command"] is False


@pytest.mark.asyncio
async def test_search__with_no_queries__expect_error_reply():
    ctx = MagicMock()
    ctx.reply = AsyncMock()

    await search_extension.search.callback(ctx)

    ctx.reply.assert_awaited_once_with("You must provide at least one filter.")


@pytest.mark.asyncio
async def test_search__with_unknown_field__expect_error_reply():
    ctx = MagicMock()
    ctx.reply = AsyncMock()

    try:
        await search_extension.search.callback(ctx, "unknown=value")
    except ValueError as e:
        await search_extension.search_error(ctx, e)

    ctx.reply.assert_awaited_once()
    assert "Unknown field" in ctx.reply.call_args.args[0]


@pytest.mark.asyncio
async def test_search__with_no_results__expect_no_results_reply():
    ctx = MagicMock()
    ctx.reply = AsyncMock()

    mock_query = MagicMock()
    mock_query.where.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []

    with patch.object(
        search_extension.Message, "where", create=True, return_value=mock_query
    ):
        await search_extension.search.callback(ctx, "content=hello")

    ctx.reply.assert_awaited_once_with("No results found.")


@pytest.mark.asyncio
async def test_search__with_results__expect_results_reply():
    ctx = MagicMock()
    ctx.reply = AsyncMock()

    msg1 = MagicMock()
    msg1.content = "hello"
    msg1.url = "https://matrix.to/#/!room:server/$event1"

    msg2 = MagicMock()
    msg2.content = "world"
    msg2.url = "https://matrix.to/#/!room:server/$event2"

    mock_query = MagicMock()
    mock_query.where.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [msg1, msg2]

    with patch.object(
        search_extension.Message, "where", create=True, return_value=mock_query
    ):
        await search_extension.search.callback(ctx, "content=o")

    ctx.reply.assert_awaited_once()
    reply_text = ctx.reply.call_args.args[0]

    assert "Search results (2):" in reply_text
    assert "[hello](<https://matrix.to/#/!room:server/$event1>)" in reply_text
    assert "[world](<https://matrix.to/#/!room:server/$event2>)" in reply_text


@pytest.mark.asyncio
async def test_search_error__with_value_error__expect_error_message_reply():
    ctx = MagicMock()
    ctx.reply = AsyncMock()

    await search_extension.search_error(ctx, ValueError("Invalid query"))
    ctx.reply.assert_awaited_once_with("Invalid query")
