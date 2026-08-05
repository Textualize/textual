"""Regression test for the input thread when stdin reaches end-of-file.

A selector reports a file descriptor at EOF as readable, so `select()` returns
immediately, forever. Unless the input thread notices the EOF and stops
selecting, it busy-loops and pegs a CPU core for the life of the app.

Asserting the thread returns is a deterministic stand-in for measuring CPU: a
thread that has returned cannot busy-loop.
"""

import os
import signal
import sys
import threading
from typing import Iterator

import pytest

from textual.app import App
from textual.driver import Driver

if sys.platform == "win32":
    pytest.skip("LinuxDriver/LinuxInlineDriver are POSIX only", allow_module_level=True)

from textual.drivers.linux_driver import LinuxDriver
from textual.drivers.linux_inline_driver import LinuxInlineDriver


@pytest.fixture
def eof_fileno() -> Iterator[int]:
    """A file descriptor permanently at EOF, like stdin whose terminal is gone."""
    read_fd, write_fd = os.pipe()
    os.close(write_fd)
    try:
        yield read_fd
    finally:
        os.close(read_fd)


@pytest.fixture
def preserve_signal_handlers() -> Iterator[None]:
    """Restore the handlers that `LinuxDriver.__init__` installs."""
    saved = {
        number: signal.getsignal(number) for number in (signal.SIGTSTP, signal.SIGCONT)
    }
    try:
        yield
    finally:
        for number, handler in saved.items():
            if handler is not None:
                signal.signal(number, handler)


@pytest.mark.parametrize("driver_class", [LinuxDriver, LinuxInlineDriver])
async def test_input_thread_stops_on_stdin_eof(
    driver_class: type[Driver],
    eof_fileno: int,
    preserve_signal_handlers: None,
) -> None:
    async with App().run_test() as pilot:
        driver = driver_class(pilot.app)
        driver.fileno = eof_fileno

        thread = threading.Thread(target=driver.run_input_thread, daemon=True)
        thread.start()
        thread.join(timeout=5.0)
        spinning = thread.is_alive()
        if spinning:
            # Stop the thread before the fixture closes the descriptor under it.
            driver.exit_event.set()
            thread.join(timeout=5.0)

        assert not spinning, "input thread is busy-looping on a stdin that is at EOF"
