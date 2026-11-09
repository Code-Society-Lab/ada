from dataclasses import dataclass

import dachshund

EMA_ALPHA = 0.2


@dataclass
class LatencyHealth:
    """A running average (EMA) of the scheduled latency checks, recent ones weighing most."""

    average_ms: float | None = None

    async def load(self) -> None:
        """Rebuild the average from the stored latency checks."""
        self.average_ms = None

        for event in await dachshund.default().events.events("latency"):
            value = event.payload.get("check")

            if value is not None:
                self._accumulate(value)

        if self.average_ms is not None:
            dachshund.emit("average_latency", value=self.average_ms)

    def record_check(self, latency_ms: int) -> None:
        """A scheduled round trip to the homeserver, which the health tracks."""
        dachshund.emit("latency", check=latency_ms, message=None)
        self._accumulate(latency_ms)
        dachshund.emit("average_latency", value=self.average_ms)

    def record_message(self, latency_ms: int) -> None:
        """A message's delivery delay, shown live but left out of the health."""
        dachshund.emit("latency", check=None, message=latency_ms)

    def _accumulate(self, latency_ms: float) -> None:
        if self.average_ms is None:
            self.average_ms = latency_ms
        else:
            self.average_ms += EMA_ALPHA * (latency_ms - self.average_ms)
