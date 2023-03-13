import asyncio

from ._time import time

"""
A module that serves as the single source of truth for everything time-related in a Textual app.
Having this logic centralised makes it easier to simulate time in integration tests,
by mocking the few functions exposed by this module.
"""


# N.B. This class and its singleton instance have to be hidden APIs because we want to be able to mock time,
# even for Python modules that imported functions such as `get_time` *before* we mocked this internal _Clock.
# (so mocking public APIs such as `get_time` wouldn't affect direct references to then that were done during imports)
class _Clock:
    async def get_time(self) -> float:
        return time()


_clock = _Clock()


async def get_time() -> float:
    """
    Asynchronous version of `get_time`. Useful in situations where we want asyncio to be
    able to "do things" elsewhere right before we fetch the time.

    Returns:
        The value (in fractional seconds) of a monotonic clock, i.e. a clock that cannot go backwards.
    """
    return await _clock.get_time()
