"""Code to help calculate the estimated time to completion of some process."""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from rich.repr import Result
from typing_extensions import Self


@dataclass
class Sample:
    """A sample."""

    value: float
    """The value of the sample."""

    moment: float
    """The moment when the sample was taken."""


class Samples:
    """A deque-ish-like object that holds samples."""

    def __init__(self, time_window_size: float, max_samples: int) -> None:
        """Initialise the samples object.

        Args:
            time_window_size: The window of time to keep samples for.
            max_samples: The maximum number of samples to keep.
        """
        self._time_window_size = time_window_size
        """The maximum amount of time to keep the samples for."""
        self._max_samples = max_samples
        """The maximum number of samples to keep."""
        self._samples: list[Sample] = []
        """The samples."""
        self._last_dropped: Sample | None = None
        """Keep track of the last-dropped sample."""

    def _prune(self) -> Self:
        """Prune the samples.

        Note:
            While there is a sample limit *and* a time limit, we only prune
            by one or the other, and sample size always trumps time, to help
            ensure we have *some* samples to work off.
        """
        if samples := self._samples:
            # Trim off any "too old" samples.
            oldest_time = samples[-1].moment - self._time_window_size
            for position, sample in enumerate(samples):
                if sample.moment > oldest_time:
                    # We keep the "last dropped" sample around for any sort
                    # of fallback position.
                    self._last_dropped = samples[position - 1]
                    self._samples = samples[position:]
                    break
            # Ensure that we don't run up too many samples.
            self._samples = self._samples[-self._max_samples :]
        return self

    def append(self, sample: Sample) -> Self:
        """Add a sample to the samples.

        Args:
            sample: The sample to add.

        Returns:
            Self.
        """
        self._samples.append(sample)
        return self._prune()

    def clear(self) -> Self:
        """Clear the samples."""
        self._samples.clear()
        return self

    @property
    def last_dropped(self) -> Sample | None:
        """The last sample to be dropped out of the time window.

        If none has been dropped yet then `None`.
        """
        return self._last_dropped

    def __getitem__(self, index: int) -> Sample:
        return self._samples[index]

    def __len__(self) -> int:
        return len(self._samples)

    def __rich_repr__(self) -> Result:
        yield self._samples


class TimeToCompletion:
    """A class for calculating the time to completion of something.

    A utility class designed to help calculate the time to completion of a
    series of points that happen over time. Values recorded are assumed to
    be >= 0.
    """

    def __init__(
        self,
        destination: float,
        *,
        time_window_size: float = 30,
        max_samples: int = 1_000,
    ) -> None:
        """Initialise the time to completion object.

        Args:
            destination: The destination value.
            time_window_size: The size of the time window to work off.
            max_samples: The maximum number of samples to retain.
        """
        self._destination = destination
        """The destination value."""
        self._samples = Samples(time_window_size, max_samples)
        """The samples taken."""

    def __len__(self) -> int:
        """The count of samples."""
        return len(self._samples)

    def reset(self) -> Self:
        """Reset the samples."""
        self._samples.clear()
        return self

    def record(self, value: float, at_time: float | None = None) -> Self:
        """Record a value.

        Args:
            value: The value to record.
            at_time: The time point at which to make the record.

        Returns:
            Self.
        """
        # If the last sample is higher in value than the new one...
        if self._samples and self._samples[-1].value > value:
            # ...treat that as an error.
            raise ValueError(f"{value} is less than the previously-recorded value")
        # If the sample is higher than the destination...
        if value > self._destination:
            raise ValueError(
                f"{value} is greater than the destination of {self._destination}"
            )
        # Record the new sample.
        self._samples.append(Sample(value, monotonic() if at_time is None else at_time))
        return self

    @property
    def _oldest_sample(self) -> Sample | None:
        """The oldest sample we have, if there is one.

        For cases where all sample but the most recent one have expired out
        of the window, the oldest sample will be the last-dropped sample.
        This will help give a best guess as to hold long what's left may
        take.
        """
        if (samples := len(self._samples)) > 1:
            # We have multiple samples, so return the oldest.
            return self._samples[0]
        elif samples == 1 and (last_dropped := self._samples.last_dropped) is not None:
            # We only have the one sample, but we do have a reference the
            # the last-dropped sample, so as a fallback use that.
            return last_dropped
        # We don't have any samples to go off.
        return None

    @property
    def _elapsed(self) -> float:
        """The time elapsed over the course of the samples.

        Note that this is the time elapsed over all of the recorded samples,
        not from the first until now.
        """
        if (oldest := self._oldest_sample) is not None:
            return self._samples[-1].moment - oldest.moment
        return 0

    @property
    def _elapsed_to_now(self) -> float:
        """The time elapsed over the course of the samples until now.

        This will always be 0 if no samples have been recorded yet.
        """
        if (oldest := self._oldest_sample) is not None:
            return monotonic() - oldest.moment
        return 0

    @property
    def _distance_covered_in_window(self) -> float:
        """The distance covered by the samples.

        Note that this is just the distance covered by the samples in the
        current window; not the distance covered by every sample that has
        been recorded.
        """
        if (oldest := self._oldest_sample) is not None:
            return self._samples[-1].value - oldest.value
        return 0

    @property
    def _distance_remaining(self) -> float:
        """The distance remaining until the destination is reached."""
        return self._destination - (self._samples[-1].value if len(self) else 0)

    @property
    def _speed(self) -> float:
        """The speed based on the recorded samples."""
        try:
            return self._elapsed / self._distance_covered_in_window
        except ZeroDivisionError:
            return self._elapsed

    @property
    def _speed_now(self) -> float:
        """The speed as of right now, based on the recorded samples."""
        try:
            return self._elapsed_to_now / self._distance_covered_in_window
        except ZeroDivisionError:
            return self._elapsed_to_now

    @property
    def estimated_time_to_complete(self) -> float:
        """The estimated time to completion.

        This is the time as of the last-recorded sample.
        """
        return self._distance_remaining * self._speed

    @property
    def estimated_time_to_complete_as_of_now(self) -> float:
        """The estimated time to completion as of now."""
        return self._distance_remaining * self._speed_now

    def __rich_repr__(self) -> Result:
        yield "destination", self._destination
        yield "estimated_time_to_complete", self.estimated_time_to_complete
        yield "estimated_time_to_complete_as_of_now", self.estimated_time_to_complete_as_of_now
        yield self._samples


if __name__ == "__main__":
    from time import sleep

    for portion in range(2, 21):
        etc = TimeToCompletion(500)
        started = monotonic()
        for n in range(500 // portion):
            etc.record(n)
            sleep(0.01)
        elapsed = monotonic() - started
        print(f"==== Based on 1/{portion} of the full range ====")
        print(f"Elapsed........: {elapsed}")
        print(f"ETC............: {etc.estimated_time_to_complete}")
        print(f"ETC now........: {etc.estimated_time_to_complete_as_of_now}")
        print(f"Estimated total: {etc.estimated_time_to_complete + elapsed}")
