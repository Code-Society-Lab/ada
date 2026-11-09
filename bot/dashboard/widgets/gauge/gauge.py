from dataclasses import KW_ONLY, dataclass
from pathlib import Path
from typing import Any, ClassVar

from dachshund.widgets import AggregatedWidget


@dataclass
class Gauge(AggregatedWidget):
    """A number of its source, as an arc gauge with green/amber/red zones.

    Takes `y`, `aggregate` and `over` like `Number`. `warning_at`/`critical_at`
    default to 60%/85% of the way across `[min, max]` when not given.

    ## Example

    ```python
    Gauge("latency", aggregate="average", over=timedelta(hours=1), max=500, unit="ms")
    ```
    """

    _: KW_ONLY

    min: float = 0
    max: float = 100
    warning_at: float | None = None
    critical_at: float | None = None
    unit: str | None = None

    type: ClassVar[str] = "gauge"
    op: ClassVar[str] = "replace"
    script: ClassVar[Path] = Path(__file__).parent / "gauge.js"
    style: ClassVar[Path] = Path(__file__).parent / "gauge.css"

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.max <= self.min:
            raise ValueError("A gauge's max must be greater than its min.")

        span = self.max - self.min

        if self.warning_at is None:
            self.warning_at = self.min + span * 0.6
        if self.critical_at is None:
            self.critical_at = self.min + span * 0.85

    def render_value(self, value: float | None) -> dict[str, Any]:
        """`value`, plus the range/zone config the arc needs."""
        return {
            "value": value,
            "min": self.min,
            "max": self.max,
            "warning_at": self.warning_at,
            "critical_at": self.critical_at,
            "unit": self.unit,
        }
