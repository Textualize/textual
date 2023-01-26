from asyncio import sleep
from time import process_time, time


SLEEP_GRANULARITY: float = 1 / 50
SLEEP_IDLE: float = SLEEP_GRANULARITY / 2.0


async def wait_for_idle(min_sleep: float = 0.01, max_sleep: float = 1) -> None:
    """Wait until the cpu isn't working very hard.

    Args:
        min_sleep: Minimum time to wait. Defaults to 0.01.
        max_sleep: Maximum time to wait. Defaults to 1.
    """
    start_time = time()

    while True:
        cpu_time = process_time()
        await sleep(SLEEP_GRANULARITY)
        cpu_elapsed = process_time() - cpu_time
        elapsed_time = time() - start_time
        if elapsed_time >= max_sleep:
            break
        if elapsed_time > min_sleep and cpu_elapsed < SLEEP_IDLE:
            break
