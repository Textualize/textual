import os
import sys
from ctypes.wintypes import DWORD
from threading import Event
from typing import Iterator

from . import win32

WAIT_FAILED = 0xFFFFFFFF
WAIT_TIMEOUT = 0x00000102
WAIT_OBJECT_0 = 0x00000000
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11


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

        timeout_milliseconds = DWORD(int(self.timeout * 1000))

        WaitForSingleObject = win32.KERNEL32.WaitForSingleObject
        GetStdHandle = win32.GetStdHandle

        stdin_handle = GetStdHandle(STD_INPUT_HANDLE)
        while not self._exit_event.is_set():
            result = WaitForSingleObject(
                stdin_handle,
                timeout_milliseconds,
            )
            if result == WAIT_TIMEOUT:
                continue
            if result == WAIT_OBJECT_0:
                data = os.read(self._fileno, 1024) or None
                if data is None:
                    break
                yield data
