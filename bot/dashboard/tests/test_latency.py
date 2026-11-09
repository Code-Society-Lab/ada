from collections.abc import Iterator
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from bot.dashboard import latency
from bot.dashboard.latency import LatencyHealth


@pytest.fixture
def emit() -> Iterator[MagicMock]:
    with patch.object(latency.dachshund, "emit") as mock:
        yield mock


def test_first_check_is_the_average(emit: MagicMock) -> None:
    health = LatencyHealth()
    health.record_check(100)

    assert health.average_ms == 100
    emit.assert_has_calls(
        [
            call("latency", check=100, message=None),
            call("average_latency", value=100),
        ]
    )


def test_later_checks_move_average_by_alpha(emit: MagicMock) -> None:
    health = LatencyHealth()
    health.record_check(100)
    health.record_check(200)

    assert health.average_ms == pytest.approx(120)


def test_message_latency_is_shown_but_left_out_of_health(emit: MagicMock) -> None:
    health = LatencyHealth(average_ms=100)
    health.record_message(900)

    assert health.average_ms == 100
    emit.assert_called_once_with("latency", check=None, message=900)


async def test_load_replays_stored_readings(emit: MagicMock) -> None:
    stored = [
        SimpleNamespace(payload={"check": 100, "message": None}),
        SimpleNamespace(payload={"check": None, "message": 900}),
        SimpleNamespace(payload={"check": 200, "message": None}),
    ]
    store = SimpleNamespace(
        events=SimpleNamespace(events=AsyncMock(return_value=stored))
    )

    with patch.object(latency.dachshund, "default", return_value=store):
        health = LatencyHealth(average_ms=999)
        await health.load()

    assert health.average_ms == pytest.approx(120)
    emit.assert_called_once_with("average_latency", value=pytest.approx(120))


async def test_load_without_readings_emits_nothing(emit: MagicMock) -> None:
    store = SimpleNamespace(events=SimpleNamespace(events=AsyncMock(return_value=[])))

    with patch.object(latency.dachshund, "default", return_value=store):
        health = LatencyHealth()
        await health.load()

    assert health.average_ms is None
    emit.assert_not_called()
