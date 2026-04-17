import logging
from typing import Iterable

from matrix import Extension, Room, Context
from nio import RoomMessageText
from sqlalchemy import ColumnElement

from .fields import SEARCH_FIELDS
from .message import Message

# This is temporary until we add paging
_MAX_RESULTS = 50
_FIELDS_HELP = "\n".join(
    f"  • `{name}=<value>` — {field.description}"
    for name, field in SEARCH_FIELDS.items()
)


logger = logging.getLogger(__name__)
extension = Extension("search")


@extension.event
async def on_message(room: Room, event: RoomMessageText) -> None:
    message = Message.create(
        content=event.body,
        timestamp=event.server_timestamp,
        sender=event.sender,
        event_id=event.event_id,
        room_id=room.room_id,
        is_command=event.body.startswith(extension.bot.prefix),
    )
    logger.debug(f"Message saved: {message}")


@extension.command(
    usage='search field="value"',
    description=(
        "Search stored messages in the room.\n\n"
        f"Supported fields:\n{_FIELDS_HELP}\n\n"
        "Multiple filters are combined with AND logic."
    ),
)
async def search(ctx: Context, *queries: str) -> None:
    if not queries:
        await ctx.reply("You must provide at least one filter.")
        return

    clauses = _build_clauses(queries)
    messages = (
        Message.where(*clauses)
        .where(room_id=ctx.room.room_id)
        .limit(_MAX_RESULTS)
        .all()
    )

    if not messages:
        await ctx.reply("No results found.")
        return

    body = "\n".join(f"[{msg.content}](<{msg.url}>)" for msg in messages)
    await ctx.reply(f"Search results ({len(messages)}):\n{body}")


@search.error(exception=ValueError)
async def search_error(ctx: Context, error: ValueError) -> None:
    await ctx.reply(str(error))


def _build_clauses(queries: tuple[str, ...]) -> list[ColumnElement[bool]]:
    terms = list(_extract_search_terms(queries))
    mentioned = {name for name, _ in terms}
    return _clauses_from_terms(terms) + _default_clauses(mentioned)


def _clauses_from_terms(terms: list[tuple[str, str]]) -> list[ColumnElement[bool]]:
    clauses = []
    for field_name, value in terms:
        search_field = SEARCH_FIELDS.get(field_name)
        if search_field is None:
            raise ValueError(
                f"Unknown field: `{field_name}`. Valid fields: {', '.join(SEARCH_FIELDS)}"
            )
        clauses.append(search_field.build_clause(value))
    return clauses


def _default_clauses(mentioned: set[str]) -> list[ColumnElement[bool]]:
    return [
        field.build_clause(field.default)
        for name, field in SEARCH_FIELDS.items()
        if name not in mentioned and field.default is not None
    ]


def _extract_search_terms(queries: tuple[str, ...]) -> Iterable[tuple[str, str]]:
    for query in queries:
        if "=" not in query:
            raise ValueError(f"Invalid query format: `{query}`. Use field=value")
        field_name, value = query.split("=", 1)
        if not value:
            raise ValueError(
                f"Empty value for field: `{field_name}`. Provide a value or remove the filter."
            )
        yield field_name, value
