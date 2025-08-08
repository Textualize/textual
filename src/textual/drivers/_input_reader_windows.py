import os
import sys
from queue import Empty, Queue
from threading import Event, Thread
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
        self._queue: Queue | None = None
        self._worker_thread: Thread = Thread(
            target=self._run_worker_thread, name="input-reader-worker"
        )

    def close(self) -> None:
        """Close the reader (will exit the iterator)."""
        self._exit_event.set()

    def _run_worker_thread(self) -> None:
        while not self._exit_event.is_set():
            try:
                data = os.read(self._fileno, 1024) or None
            except Exception:
                data = None
            self._queue.put(data)
            if not data:
                break

    def __iter__(self) -> Iterator[bytes]:
        """Read input, yield bytes."""
        if self._queue is None:
            self._queue = Queue(maxsize=1)
            self._worker_thread.start()
        while not self._exit_event.is_set():
            try:
                data = self._queue.get(timeout=self.timeout)
            except Empty:
                yield b""
            else:
                if not data:
                    return
                yield data
