import os
import sys
from ctypes import byref, wintypes
from threading import Event
from typing import Iterator

from . import win32


class InputReader:
    """Read input from stdin."""

    def __init__(self, timeout: float = 0.1) -> None:
        """

        Args:
            timeout: Seconds to block for input.
        """
        self._fileno = sys.__stdin__.fileno()
        self.timeout = timeout
        self._exit_event = Event()

    def more_data(self) -> bool:
        """Check if there is data pending."""
        return True

    def close(self) -> None:
        """Close the reader (will exit the iterator)."""
        self._exit_event.set()

    def __iter__(self) -> Iterator[bytes]:
        """Read input, yield bytes."""

        stdin = sys.__stdin__

        current_console_mode_in = win32.get_console_mode(stdin)

        def restore() -> None:
            win32.set_console_mode(stdin, current_console_mode_in)

        MAX_EVENTS = 1024
        KEY_EVENT = 0x0001
        WINDOW_BUFFER_SIZE_EVENT = 0x0004

        arrtype = win32.INPUT_RECORD * MAX_EVENTS
        input_records = arrtype()

        ReadConsoleInputW = win32.KERNEL32.ReadConsoleInputW
        wait_for_handles = win32.wait_for_handles
        hIn = win32.GetStdHandle(win32.STD_INPUT_HANDLE)
        exit_requested = self._exit_event.is_set
        timeout_milliseconds = int(self.timeout * 1000)

        read_count = wintypes.DWORD(0)

        while not exit_requested():
            if wait_for_handles([hIn], timeout_milliseconds) is None:
                continue

            ReadConsoleInputW(hIn, byref(input_records), MAX_EVENTS, byref(read_count))
