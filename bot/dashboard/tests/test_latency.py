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


def test_first_reading_is_the_average(emit: MagicMock) -> None:
    health = LatencyHealth()
    health.record(100)

    assert health.average_ms == 100
    emit.assert_has_calls(
        [call("latency", value=100), call("average_latency", value=100)]
    )


def test_later_readings_move_average_by_alpha(emit: MagicMock) -> None:
    health = LatencyHealth()
    health.record(100)
    health.record(200)

    assert health.average_ms == pytest.approx(120)


async def test_load_replays_stored_readings(emit: MagicMock) -> None:
    stored = [SimpleNamespace(payload={"value": v}) for v in (100, None, 200)]
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
