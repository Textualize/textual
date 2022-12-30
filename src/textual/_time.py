import platform

from asyncio import sleep as asyncio_sleep, get_running_loop
from time import monotonic, perf_counter, sleep as time_sleep


PLATFORM = platform.system()
WINDOWS = PLATFORM == "Windows"


if WINDOWS:
    time = perf_counter
else:
    time = monotonic


if WINDOWS:

    async def sleep(sleep_for: float) -> None:
        """An asyncio sleep.

        On Windows this achieves a better granularity that asyncio.sleep

        Args:
            sleep_for (float): Seconds to sleep for.
        """
        await get_running_loop().run_in_executor(None, time_sleep, sleep_for)

else:
    sleep = asyncio_sleep
