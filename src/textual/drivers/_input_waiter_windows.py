"""
Windows InputWaiter, which uses the win32 API for wait for a file.

"""

import ctypes

kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]

WAIT_FAILED = 0xFFFFFFFF


class InputWaiter:
    """Object to wait for input from a file handle."""

    def __init__(self, fileno: int) -> None:
        """

        Args:
            fileno: File number / handle.
        """
        self._fileno = fileno

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
        return (
            kernel32.WaitForSingleObject(self._fileno, timeout_milliseconds)
            != WAIT_FAILED
        )

    def close(self) -> None:
        """Close the object."""
