"""
A version of `time.sleep` that is more accurate than the standard library (even on Python 3.11).

This should only be imported on Windows.
"""

from __future__ import annotations

import asyncio
from time import sleep as time_sleep
from typing import Coroutine

__all__ = ["sleep"]


INFINITE = 0xFFFFFFFF
WAIT_FAILED = 0xFFFFFFFF
CREATE_WAITABLE_TIMER_HIGH_RESOLUTION = 0x00000002
TIMER_ALL_ACCESS = 0x1F0003


async def time_sleep_coro(secs: float):
    """Coroutine wrapper around `time.sleep`."""
    await asyncio.sleep(secs)


try:
    import ctypes
    from ctypes.wintypes import HANDLE, LARGE_INTEGER

    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
except Exception:

    def sleep(secs: float) -> Coroutine[None, None, None]:
        """Wrapper around `time.sleep` to match the signature of the main case below."""
        return time_sleep_coro(secs)

else:

    async def no_sleep_coro():
        """Creates a coroutine that does nothing for when no sleep is needed."""
        pass

    def sleep(secs: float) -> Coroutine[None, None, None]:
        """A replacement sleep for Windows.

        Note that unlike `time.sleep` this *may* sleep for slightly less than the
        specified time. This is generally not an issue for Textual's use case.

        In order to create a timer that _can_ be cancelled on Windows, we need to
        create a timer and a separate event, and then we wait for either of the two
        things. When Textual wants to quit, we set the cancel event.

        Args:
            secs: Seconds to sleep for.
        """

        # Subtract a millisecond to account for overhead
        sleep_for = max(0, secs - 0.001)
        if sleep_for < 0.0005:
            # Less than 0.5ms and its not worth doing the sleep
            return no_sleep_coro()

        timer = kernel32.CreateWaitableTimerExW(
            None,
            None,
            CREATE_WAITABLE_TIMER_HIGH_RESOLUTION,
            TIMER_ALL_ACCESS,
        )
        if not timer:
            return time_sleep_coro(sleep_for)

        if not kernel32.SetWaitableTimer(
            timer,
            ctypes.byref(LARGE_INTEGER(int(sleep_for * -10_000_000))),
            0,
            None,
            None,
            0,
        ):
            kernel32.CloseHandle(timer)
            return time_sleep_coro(sleep_for)

        cancel_event = kernel32.CreateEventExW(None, None, 0, TIMER_ALL_ACCESS)
        if not cancel_event:
            kernel32.CloseHandle(timer)
            return time_sleep_coro(sleep_for)

        def cancel_inner():
            """Sets the cancel event so we know we can stop waiting for the timer."""
            kernel32.SetEvent(cancel_event)

        async def cancel():
            """Cancels the timer by setting the cancel event."""
            await asyncio.get_running_loop().run_in_executor(None, cancel_inner)

        def wait_inner():
            """Function responsible for waiting for the timer or the cancel event."""
            if (
                kernel32.WaitForMultipleObjects(
                    2,
                    ctypes.pointer((HANDLE * 2)(cancel_event, timer)),
                    False,
                    INFINITE,
                )
                == WAIT_FAILED
            ):
                time_sleep(sleep_for)

        async def wait():
            """Wraps the actual sleeping so we can detect if the thread was cancelled."""
            try:
                await asyncio.get_running_loop().run_in_executor(None, wait_inner)
            except asyncio.CancelledError:
                await cancel()
                raise
            finally:
                kernel32.CloseHandle(timer)
                kernel32.CloseHandle(cancel_event)

        return wait()
