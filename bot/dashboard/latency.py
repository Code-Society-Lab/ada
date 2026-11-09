from dataclasses import dataclass

import dachshund

EMA_ALPHA = 0.2


@dataclass
class LatencyHealth:
    """A running average of latency, weighting recent readings most (EMA)."""

    average_ms: float | None = None

    async def load(self) -> None:
        """Rebuild the average from the stored latency readings."""
        self.average_ms = None

        for event in await dachshund.default().events.events("latency"):
            value = event.payload.get("value")

            if value is not None:
                self._accumulate(value)

        if self.average_ms is not None:
            dachshund.emit("average_latency", value=self.average_ms)

    def record(self, latency_ms: int) -> None:
        dachshund.emit("latency", value=latency_ms)
        self._accumulate(latency_ms)
        dachshund.emit("average_latency", value=self.average_ms)

    def _accumulate(self, latency_ms: float) -> None:
        if self.average_ms is None:
            self.average_ms = latency_ms
        else:
            self.average_ms += EMA_ALPHA * (latency_ms - self.average_ms)
