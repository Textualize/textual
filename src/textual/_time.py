import platform

from asyncio import sleep as asleep
from time import monotonic, perf_counter

PLATFORM = platform.system()
WINDOWS = PLATFORM == "Windows"


if WINDOWS:
    time = perf_counter
else:
    time = monotonic


if WINDOWS:

    async def sleep(sleep_for: float) -> None:
        """An asyncio sleep.

        On Windows this achieves a better granularity that asyncio.sleep(0)

        Args:
            sleep_for (float): Seconds to sleep for.
        """
        start = time()
        while time() - start < sleep_for - 1 / 1000:
            await asleep(0)

else:
    sleep = asleep
