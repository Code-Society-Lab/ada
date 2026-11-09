from datetime import timedelta

import pytest

from bot.dashboard.widgets.gauge import Gauge


def test_zones_default_to_share_of_range() -> None:
    gauge = Gauge("latency", min=0, max=200)

    assert gauge.warning_at == 120
    assert gauge.critical_at == 170


def test_rejects_empty_range() -> None:
    with pytest.raises(ValueError):
        Gauge("latency", min=10, max=10)


def test_render_value_carries_zone_config() -> None:
    gauge = Gauge(
        "latency",
        aggregate="average",
        over=timedelta(hours=1),
        max=500,
        warning_at=150,
        critical_at=300,
        unit="ms",
    )

    assert gauge.render_value(42.5) == {
        "value": 42.5,
        "min": 0,
        "max": 500,
        "warning_at": 150,
        "critical_at": 300,
        "unit": "ms",
    }
