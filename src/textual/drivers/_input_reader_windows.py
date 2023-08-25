import os
import sys
from threading import Event
from typing import Iterator


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
        while not self._exit_event.is_set():
            try:
                data = os.read(self._fileno, 1024) or None
            except Exception:
                break
            if not data:
                break
            yield data
