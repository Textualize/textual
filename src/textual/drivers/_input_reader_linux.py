import os
import selectors
import sys
from threading import Event
from typing import Iterator

from textual import log


class InputReader:
    """Read input from stdin."""

    def __init__(self, timeout: float = 0.1) -> None:
        """

        Args:
            timeout: Seconds to block for input.
        """
        self._fileno = sys.__stdin__.fileno()
        self.timeout = timeout
        self._selector = selectors.DefaultSelector()
        self._selector.register(self._fileno, selectors.EVENT_READ)
        self._exit_event = Event()

    def more_data(self) -> bool:
        """Check if there is data pending."""
        EVENT_READ = selectors.EVENT_READ
        for key, events in self._selector.select(self.timeout):
            if events:
                return True
        return False

    def close(self) -> None:
        """Close the reader (will exit the iterator)."""
        self._exit_event.set()

    def __iter__(self) -> Iterator[bytes]:
        """Read input, yield bytes."""
        fileno = self._fileno
        EVENT_READ = selectors.EVENT_READ
        read = os.read
        while not self._exit_event.is_set():
            for _selector_key, mask in self._selector.select(self.timeout):
                if mask:
                    data = read(fileno, 1024)
                    if not data:
                        return
                    yield data
