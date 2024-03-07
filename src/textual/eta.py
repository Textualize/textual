import bisect
from operator import itemgetter
from time import monotonic


class ETA:
    """Calculate speed and estimate time to arrival."""

    def __init__(self, estimation_period: float = 30) -> None:
        """Create an ETA.

        Args:
            estimation_period: Period in seconds, used to calculate speed. Defaults to 30.
        """
        self.estimation_period = estimation_period
        self._start_time = monotonic()
        self._samples: list[tuple[float, float]] = [(0.0, 0.0)]

    def reset(self) -> None:
        """Start ETA calculations from current time."""
        del self._samples[:]
        self._start_time = monotonic()

    @property
    def _current_time(self) -> float:
        return monotonic() - self._start_time

    def add_sample(self, progress: float) -> None:
        """Add a new sample.

        Args:
            progress: Progress ratio (0 is start, 1 is complete).
        """
        if self._samples and self._samples[-1][1] > progress:
            # If progress goes backwards, we need to reset calculations
            self.reset()
            return
        current_time = self._current_time
        self._samples.append((current_time, progress))
        if not (len(self._samples) % 100):
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
            return self._samples[-1]
        if index == 0:
            return self._samples[0]
        time1, progress1 = self._samples[index]
        time2, progress2 = self._samples[index + 1]
        factor = (time - time1) / (time2 - time1)
        intermediate_progress = progress1 + (progress2 - progress1) * factor
        return time, intermediate_progress

    @property
    def speed(self) -> float | None:
        """The current speed, or `None` if it couldn't be calculated."""

        if len(self._samples) <= 2:
            # Need at less 2 samples to calculate speed
            return None

        recent_sample_time, progress2 = self._samples[-1]
        progress_start_time, progress1 = self._get_progress_at(
            recent_sample_time - self.estimation_period
        )
        time_delta = recent_sample_time - progress_start_time
        distance = progress2 - progress1
        speed = distance / time_delta
        return speed

    @property
    def eta(self) -> float | None:
        """Estimated seconds until completion, or `None` if no estimate can be made."""
        current_time = self._current_time
        if not self._samples:
            return None
        speed = self.speed
        if not speed:
            return None
        recent_time, recent_progress = self._samples[-1]
        time_since_sample = current_time - recent_time
        remaining = 1.0 - (recent_progress + speed * time_since_sample)
        eta = max(0, remaining / speed)
        return eta
