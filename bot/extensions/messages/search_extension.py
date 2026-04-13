import logging

from matrix import Extension, Context
from sqlalchemy import ColumnElement
from sqlmodel import col

from .message import Message

logger = logging.getLogger(__name__)

extension = Extension("search")


@extension.event
async def on_message(_room, event):
    is_command = False

    if event.body.startswith("!"):
        is_command = True

    message = Message.create(
        content=event.body,
        timestamp=event.server_timestamp,
        sender=event.sender,
        event_id=event.event_id,
        is_command=is_command,
    )

    logger.debug(f"Message saved: {message}")


@extension.command()
async def search(ctx: Context, *queries: str) -> None:
    clauses: list[ColumnElement[bool]] = []

    for field, value in _extract_search_terms(queries):
        if field == "content":
            clauses.append(col(Message.content).ilike(f"%{value}%"))
        elif field == "is_command":
            clauses.append(col(Message.is_command) == (value.lower() == "true"))
        elif hasattr(Message, field):
            clauses.append(getattr(Message, field) == value)
        else:
            await ctx.reply(f"Unknown field: `{field}`")
            return

    results = Message.where(*clauses).all()

    if not results:
        await ctx.reply("No results found.")
        return

    messages = [msg.content for msg in results]
    await ctx.reply("Search results:\n" + "\n".join(messages))


@search.error(exception=ValueError)
async def search_error(ctx: Context, error: ValueError):
    await ctx.reply(str(error))


def _extract_search_terms(queries: tuple[str, ...]) -> list[tuple[str, str]]:
    terms = []

    for query in queries:
        if "=" not in query:
            raise ValueError(f"Invalid query format: `{query}`. Use field=value")

        field, value = query.split("=", 1)

        if not value:
            continue

        terms.append((field, value))
    return terms
