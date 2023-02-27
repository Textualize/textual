"""
A version of `time.sleep` that is more accurate than the standard library (even on Python 3.11).

This should only be imported on Windows.

"""

from time import sleep as time_sleep

__all__ = ["sleep"]


INFINITE = 0xFFFFFFFF
WAIT_FAILED = 0xFFFFFFFF
CREATE_WAITABLE_TIMER_HIGH_RESOLUTION = 0x00000002
TIMER_ALL_ACCESS = 0x1F0003

try:
    import ctypes
    from ctypes.wintypes import LARGE_INTEGER

    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
except Exception:
    sleep = time_sleep
else:

    def sleep(secs: float) -> None:
        """A replacement sleep for Windows.

        Note that unlike `time.sleep` this *may* sleep for slightly less than the
        specified time. This is generally not an issue for Textual's use case.

        Args:
            secs: Seconds to sleep for.
        """

        # Subtract a millisecond to account for overhead
        sleep_for = max(0, secs - 0.001)
        if sleep_for < 0.0005:
            # Less than 0.5ms and its not worth doing the sleep
            return

        handle = kernel32.CreateWaitableTimerExW(
            None,
            None,
            CREATE_WAITABLE_TIMER_HIGH_RESOLUTION,
            TIMER_ALL_ACCESS,
        )
        if not handle:
            time_sleep(sleep_for)
            return

        try:
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
        finally:
            kernel32.CloseHandle(handle)
