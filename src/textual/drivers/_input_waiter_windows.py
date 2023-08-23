"""
Windows InputWaiter, which uses the win32 API for wait for a file.

"""

import ctypes
from ctypes.wintypes import DWORD

kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]

GetStdHandle = kernel32.GetStdHandle

WAIT_FAILED = 0xFFFFFFFF
WAIT_TIMEOUT = 0x00000102
WAIT_OBJECT_0 = 0x00000000
STD_INPUT_HANDLE = -10


class InputWaiter:
    """Object to wait for input from a file handle."""

    def __init__(self, fileno: int) -> None:
        """

        Args:
            fileno: File number / handle.
        """

    def more_data(self) -> bool:
        """Check if there is data pending."""
        ...
        return False

    def wait(self, timeout: float = 0.1) -> bool:
        """Wait for input.

        Args:
            timeout: Timeout before returning.

        Returns:
            True if there is data to be read, otherwise False if a timeout occurred.
        """
        timeout_milliseconds = int(timeout * 1000)

        hIn = GetStdHandle(STD_INPUT_HANDLE)
        result = kernel32.WaitForSingleObject(hIn, DWORD(timeout_milliseconds))
        if result == WAIT_TIMEOUT:
            return False
        return True

    def close(self) -> None:
        """Close the object."""


if __name__ == "__main__":
    import sys

    fileno = sys.__stdin__.fileno()
    import os

    while 1:
        hIn = GetStdHandle(STD_INPUT_HANDLE)
        result = kernel32.WaitForSingleObject(fileno, DWORD(500))
        print(result)
        print(os.read(fileno, 1024))
