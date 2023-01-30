from asyncio import sleep
from time import process_time, monotonic

SLEEP_GRANULARITY: float = 1 / 50
SLEEP_IDLE: float = SLEEP_GRANULARITY / 2.0


async def wait_for_idle(
    min_sleep: float = SLEEP_GRANULARITY, max_sleep: float = 1
) -> None:
    """Wait until the cpu isn't working very hard.

    Args:
        min_sleep: Minimum time to wait.
        max_sleep: Maximum time to wait.
    """
    start_time = monotonic()

    while True:
        cpu_time = process_time()
        await sleep(SLEEP_GRANULARITY)
        cpu_elapsed = process_time() - cpu_time
        elapsed_time = monotonic() - start_time
        if elapsed_time >= max_sleep:
            break
        if elapsed_time > min_sleep and cpu_elapsed < SLEEP_IDLE:
            break
