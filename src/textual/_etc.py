"""Code to help calculate the estimated time to completion of some process."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from time import monotonic

from typing_extensions import Self


@dataclass
class Sample:
    """A sample."""

    value: float
    """The value of the sample."""

    moment: float
    """The moment when the sample was taken."""


class TimeToCompletion:
    """A class for calculating the time to completion of something.

    A utility class designed to help calculate the time to completion of a
    series of points that happen over time. Values recorded are assumed to
    be >= 0.
    """

    def __init__(self, destination: float, window_size: int | None = 100) -> None:
        """Initialise the time to completion object.

        Args:
            destination: The destination value.
            window_size: The size of the window to work off.
        """
        self._destination = destination
        """The destination value."""
        self._samples: deque[Sample] = deque(maxlen=window_size)
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
    def _elapsed(self) -> float:
        """The time elapsed over the course of the samples.

        Note that this is the time elapsed over all of the recorded samples,
        not from the first until now.
        """
        return (
            self._samples[-1].moment - self._samples[0].moment
            if len(self._samples) > 1
            else 0
        )

    @property
    def _elapsed_to_now(self) -> float:
        """The time elapsed over the course of the samples until now.

        This will always be 0 if no samples have been recorded yet.
        """
        return monotonic() - self._samples[0].moment if self._samples else 0

    @property
    def _distance_covered_in_window(self) -> float:
        """The distance covered by the samples.

        Note that this is just the distance covered by the samples in the
        current window; not the distance covered by every sample that has
        been recorded.
        """
        return self._samples[-1].value - self._samples[0].value if len(self) > 1 else 0

    @property
    def _distance_remaining(self) -> float:
        """The distance remaining until the destination is reached."""
        return self._destination - (self._samples[-1].value if len(self) > 1 else 0)

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
