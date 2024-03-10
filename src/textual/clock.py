from __future__ import annotations

from time import monotonic
from typing import Callable

import rich.repr


@rich.repr.auto(angular=True)
class Clock:
    """An object to get relative time.

    The `time` attribute of clock will return the time in seconds since the
    Clock was created or reset.

    """

    def __init__(self, *, get_time: Callable[[], float] = monotonic) -> None:
        """Create a clock.

        Args:
            get_time: A callable to get time in seconds.
            start: Start the clock (time is 0 unless clock has been started).
        """
        self._get_time = get_time
        self._start_time = self._get_time()

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.time

    def clone(self) -> Clock:
        """Clone the Clock with an independent time."""
        return Clock(get_time=self._get_time)

    def reset(self) -> None:
        """Reset the clock."""
        self._start_time = self._get_time()

    @property
    def time(self) -> float:
        """Time since creation or reset."""
        return self._get_time() - self._start_time


class MockClock(Clock):
    """A mock clock object where the time may be explicitly set."""

    def __init__(self, time: float = 0.0) -> None:
        """Construct a mock clock."""
        self._time = time
        super().__init__(get_time=lambda: self._time)

    def clone(self) -> MockClock:
        """Clone the mocked clock (clone will return the same time as original)."""
        clock = MockClock(self._time)
        clock._get_time = self._get_time
        clock._time = self._time
        return clock

    def reset(self) -> None:
        """A null-op because it doesn't make sense to reset a mocked clock."""

    def set_time(self, time: float) -> None:
        """Set the time for the clock.

        Args:
            time: Time to set.
        """
        self._time = time

    @property
    def time(self) -> float:
        """Time since creation or reset."""
        return self._get_time()
