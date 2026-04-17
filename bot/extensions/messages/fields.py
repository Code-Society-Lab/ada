from abc import ABC, abstractmethod
from typing import Any, Callable

from sqlalchemy import ColumnElement
from sqlmodel import col

from .message import Message


class SearchField(ABC):
    def __init__(
        self, column: Any, description: str, default: str | None = None
    ) -> None:
        self._column = column
        self._description = description
        self._default = default

    @property
    def description(self) -> str:
        return self._description

    @property
    def default(self) -> str | None:
        return self._default

    @abstractmethod
    def build_clause(self, value: str) -> ColumnElement[bool]: ...


class IlikeField(SearchField):
    def build_clause(self, value: str) -> ColumnElement[bool]:
        return col(self._column).ilike(f"%{value}%")


class ExactField(SearchField):
    def __init__(
        self,
        column: Any,
        description: str,
        coerce: Callable[[str], Any] = str,
        default: str | None = None,
    ) -> None:
        super().__init__(column, description, default)
        self._coerce = coerce

    def build_clause(self, value: str) -> ColumnElement[bool]:
        return col(self._column) == self._coerce(value)


class BoolField(SearchField):
    def build_clause(self, value: str) -> ColumnElement[bool]:
        return col(self._column).is_(value.lower() == "true")


SEARCH_FIELDS: dict[str, SearchField] = {
    "content": IlikeField(
        Message.content,
        "case-insensitive substring match on the message body",
    ),
    "timestamp": ExactField(
        Message.timestamp,
        "exact match on the server timestamp (milliseconds)",
        coerce=int,
    ),
    "sender": ExactField(
        Message.sender,
        "exact match on the sender's Matrix user ID",
    ),
    "event_id": ExactField(
        Message.event_id,
        "exact match on the Matrix event ID",
    ),
    "is_command": BoolField(
        Message.is_command,
        "whether the message was a bot command (true|false) — defaults to false",
        default="false",
    ),
}

FIELDS_HELP = "\n".join(
    f"  • `{name}=<value>` — {field.description}"
    for name, field in SEARCH_FIELDS.items()
)
