import ctypes
from ctypes.wintypes import LARGE_INTEGER
from time import sleep as time_sleep


__all__ = ["sleep"]

kernel32 = ctypes.windll.kernel32

INFINITE = 0xFFFFFFFF
WAIT_FAILED = 0xFFFFFFFF
CREATE_WAITABLE_TIMER_HIGH_RESOLUTION = 0x00000002



def sleep(sleep_for: float) -> None:
    """A replacement sleep for Windows.

    Python 3.11 added a more accurate sleep. This may be used on < Python 3.11

    Args:
        sleep_for (float): Seconds to sleep for.
    """

    # Subtract a millisecond to account for overhead
    sleep_for = max(0, sleep_for - 0.001)
    if sleep_for < 0.0005:
        # Less than 0.5ms and its not worth doing the sleep
        return

    handle = kernel32.CreateWaitableTimerExW(
        None,
        None,
        CREATE_WAITABLE_TIMER_HIGH_RESOLUTION,
        0x1F0003,
    )
    if not handle:
        time_sleep(sleep_for)
        return

    if not kernel32.SetWaitableTimer(
        handle,
        ctypes.byref(LARGE_INTEGER(int(sleep_for * -10_000_000))),
        0,
        None,
        None,
        0,
    ):
        kernel32.CloseHandle(handle)
        time_sleep(sleep_for)
        return

    if kernel32.WaitForSingleObject(handle, INFINITE) == WAIT_FAILED:
        time_sleep(sleep_for)
    kernel32.CloseHandle(handle)
