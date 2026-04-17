import pytest
from sqlalchemy import BinaryExpression

from bot.extensions.messages.fields import SEARCH_FIELDS, FIELDS_HELP


def test_content_field__builds_ilike_clause():
    clause = SEARCH_FIELDS["content"].build_clause("hello")
    assert isinstance(clause, BinaryExpression)


def test_timestamp_field__builds_equality_clause_with_int():
    clause = SEARCH_FIELDS["timestamp"].build_clause("1234567890")
    assert isinstance(clause, BinaryExpression)


def test_timestamp_field__with_non_numeric_value__raises_value_error():
    with pytest.raises(ValueError):
        SEARCH_FIELDS["timestamp"].build_clause("not-a-number")


def test_sender_field__builds_equality_clause():
    clause = SEARCH_FIELDS["sender"].build_clause("@user:matrix.org")
    assert isinstance(clause, BinaryExpression)


def test_event_id_field__builds_equality_clause():
    clause = SEARCH_FIELDS["event_id"].build_clause("$event123")
    assert isinstance(clause, BinaryExpression)


def test_is_command_field__builds_bool_clause():
    clause = SEARCH_FIELDS["is_command"].build_clause("true")
    assert isinstance(clause, BinaryExpression)


def test_is_command_field__has_default():
    assert SEARCH_FIELDS["is_command"].default == "false"


def test_fields_help__contains_all_field_names():
    for name in SEARCH_FIELDS:
        assert name in FIELDS_HELP
