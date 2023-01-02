import platform
import sys

from asyncio import sleep as asyncio_sleep, get_running_loop
from time import monotonic, perf_counter

PLATFORM = platform.system()
WINDOWS = PLATFORM == "Windows"


if WINDOWS:
    time = perf_counter
else:
    time = monotonic


if WINDOWS:

    from ._win_sleep import sleep as win_sleep

    async def sleep(sleep_for: float) -> None:
        await get_running_loop().run_in_executor(None, win_sleep, sleep_for)

else:

    async def sleep(sleep_for: float) -> None:
        sleep_for -= 0.0005
        if sleep_for > 0:
            await asyncio_sleep(sleep_for)
