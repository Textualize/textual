from __future__ import annotations

import bisect
from math import ceil
from operator import itemgetter
from time import monotonic

import rich.repr


@rich.repr.auto(angular=True)
class ETA:
    """Calculate speed and estimate time to arrival."""

    def __init__(self, estimation_period: float = 60) -> None:
        """Create an ETA.

        Args:
            estimation_period: Period in seconds, used to calculate speed. Defaults to 30.
        """
        self.estimation_period = estimation_period
        self._samples: list[tuple[float, float]] = [(0.0, 0.0)]
        self._add_count = 0

    def __rich_repr__(self) -> rich.repr.Result:
        yield "speed", self.speed
        yield "eta", self.get_eta(monotonic())

    @property
    def first_sample(self) -> tuple[float, float]:
        """First sample, or `None` if no samples."""
        assert self._samples, "Assumes samples not empty"
        return self._samples[0]

    @property
    def last_sample(self) -> tuple[float, float]:
        """Last sample, or `None` if no samples."""
        assert self._samples, "Assumes samples not empty"
        return self._samples[-1]

    def reset(self) -> None:
        """Start ETA calculations from current time."""
        del self._samples[:]

    def add_sample(self, time: float, progress: float) -> None:
        """Add a new sample.

        Args:
            time: Time when sample occurred.
            progress: Progress ratio (0 is start, 1 is complete).
        """
        if self._samples and self.last_sample[1] > progress:
            # If progress goes backwards, we need to reset calculations
            self.reset()
            return
        self._samples.append((time, progress))
        self._add_count += 1
        if self._add_count % 100 == 0:
            # Prune periodically so we don't accumulate vast amounts of samples
            self._prune()

    def _prune(self) -> None:
        """Prune old samples."""
        if len(self._samples) <= 10:
            # Keep at least 10 samples
            return
        prune_time = self._samples[-1][0] - self.estimation_period
        index = bisect.bisect_left(self._samples, prune_time, key=itemgetter(0))
        del self._samples[:index]

    def _get_progress_at(self, time: float) -> tuple[float, float]:
        """Get the progress at a specific time."""
        index = bisect.bisect_left(self._samples, time, key=itemgetter(0))
        if index >= len(self._samples):
            return self.last_sample
        if index == 0:
            return self.first_sample
        # Linearly interpolate progress between two samples
        time1, progress1 = self._samples[index]
        time2, progress2 = self._samples[index + 1]
        factor = (time - time1) / (time2 - time1)
        intermediate_progress = progress1 + (progress2 - progress1) * factor
        return time, intermediate_progress

    @property
    def speed(self) -> float | None:
        """The current speed, or `None` if it couldn't be calculated."""

        if len(self._samples) < 2:
            # Need at less 2 samples to calculate speed
            return None

        recent_sample_time, progress2 = self.last_sample
        progress_start_time, progress1 = self._get_progress_at(
            recent_sample_time - self.estimation_period
        )
        time_delta = recent_sample_time - progress_start_time
        distance = progress2 - progress1
        speed = distance / time_delta if time_delta else 0
        return speed

    def get_eta(self, time: float) -> int | None:
        """Estimated seconds until completion, or `None` if no estimate can be made.

        Args:
            time: Current time.
        """
        speed = self.speed
        if not speed:
            # Not enough samples to guess
            return None
        recent_time, recent_progress = self.last_sample
        time_since_sample = time - recent_time
        remaining = 1.0 - (recent_progress + speed * time_since_sample)
        eta = max(0, remaining / speed)
        return ceil(eta)
