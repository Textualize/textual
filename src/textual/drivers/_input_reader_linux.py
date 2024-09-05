import os
import selectors
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
        self._selector = selectors.DefaultSelector()
        self._selector.register(self._fileno, selectors.EVENT_READ)
        self._exit_event = Event()

    def close(self) -> None:
        """Close the reader (will exit the iterator)."""
        self._exit_event.set()

    def __iter__(self) -> Iterator[bytes]:
        """Read input, yield bytes."""
        fileno = self._fileno
        read = os.read
        exit_set = self._exit_event.is_set
        EVENT_READ = selectors.EVENT_READ
        while not exit_set():
            for _key, events in self._selector.select(self.timeout):
                if events & EVENT_READ:
                    data = read(fileno, 1024)
                    if not data:
                        return
                    yield data
            yield b""
