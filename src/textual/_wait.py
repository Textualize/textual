from asyncio import sleep
from time import monotonic, process_time

SLEEP_GRANULARITY: float = 1 / 50
SLEEP_IDLE: float = SLEEP_GRANULARITY / 10.0


async def wait_for_idle(
    min_sleep: float = SLEEP_GRANULARITY, max_sleep: float = 1
) -> None:
    """Wait until the process isn't working very hard.

    This will compare wall clock time with process time. If the process time
    is not advancing at the same rate as wall clock time it means the process is
    idle (i.e. sleeping or waiting for input).

    When the process is idle it suggests that input has been processed and the state
    is predictable enough to test.

    Args:
        min_sleep: Minimum time to wait.
        max_sleep: Maximum time to wait.
    """
    start_time = monotonic()

    while True:
        cpu_time = process_time()
        # Sleep for a predetermined amount of time
        await sleep(SLEEP_GRANULARITY)
        # Calculate the wall clock elapsed time and the process elapsed time
        cpu_elapsed = process_time() - cpu_time
        elapsed_time = monotonic() - start_time

        # If we have slept the maximum, we can break
        if elapsed_time >= max_sleep:
            break

        # If we have slept at least the minimum and the cpu elapsed is significantly less
        # than wall clock, then we can assume the process has finished working for now
        if elapsed_time > min_sleep and cpu_elapsed < SLEEP_IDLE:
            break
