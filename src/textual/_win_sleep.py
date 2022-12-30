import ctypes
from ctypes.wintypes import LARGE_INTEGER
from time import sleep as time_sleep

__all__ = ["sleep"]

kernel32 = ctypes.windll.kernel32

INFINITE = 0xFFFFFFFF
WAIT_FAILED = 0xFFFFFFFF
CREATE_WAITABLE_TIMER_HIGH_RESOLUTION = 0x00000002


def sleep(sleep_for: float) -> None:
    handle = kernel32.CreateWaitableTimerExW(
        None, None, CREATE_WAITABLE_TIMER_HIGH_RESOLUTION, 0x1F0003
    )
    if not handle:
        time_sleep(sleep_for)
        return

    if not kernel32.SetWaitableTimer(
        handle,
        ctypes.byref(LARGE_INTEGER(int(sleep_for * -10000))),
        0,
        None,
        None,
        0,
    ):
        time_sleep(sleep_for)
        return

    kernel32.WaitForSingleObject(handle, INFINITE)
    kernel32.CancelWaitableTimer(handle)
