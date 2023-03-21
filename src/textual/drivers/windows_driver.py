from __future__ import annotations

import asyncio
from threading import Event, Thread
from typing import IO, Callable

from .._context import active_app
from .._types import MessageTarget
from ..driver import Driver
from . import win32


class WindowsDriver(Driver):
    """Powers display and input for Windows."""

    def __init__(
        self,
        file: IO[str],
        target: "MessageTarget",
        *,
        debug: bool = False,
        size: tuple[int, int] | None = None,
    ) -> None:
        """Initialize a driver.

        Args:
            file: A file-like object open for writing unicode.
            target: The message target (expected to be the app).
            debug: Enabled debug mode.
            size: Initial size of the terminal or `None` to detect.
        """
        super().__init__(file, target, debug=debug, size=size)

        self.exit_event = Event()
        self._event_thread: Thread | None = None
        self._restore_console: Callable[[], None] | None = None

    def write(self, data: str) -> None:
        """Write data to the output device.

        Args:
            data: Raw data.
        """
        self._file.write(data)

    def _enable_mouse_support(self) -> None:
        """Enable reporting of mouse events."""
        write = self.write
        write("\x1b[?1000h")  # SET_VT200_MOUSE
        write("\x1b[?1003h")  # SET_ANY_EVENT_MOUSE
        write("\x1b[?1015h")  # SET_VT200_HIGHLIGHT_MOUSE
        write("\x1b[?1006h")  # SET_SGR_EXT_MODE_MOUSE
        self.flush()

    def _disable_mouse_support(self) -> None:
        """Disable reporting of mouse events."""
        write = self.write
        write("\x1b[?1000l")
        write("\x1b[?1003l")
        write("\x1b[?1015l")
        write("\x1b[?1006l")
        self.flush()

    def _enable_bracketed_paste(self) -> None:
        """Enable bracketed paste mode."""
        self.write("\x1b[?2004h")

    def _disable_bracketed_paste(self) -> None:
        """Disable bracketed paste mode."""
        self.write("\x1b[?2004l")

    def start_application_mode(self) -> None:
        """Start application mode."""
        loop = asyncio.get_running_loop()

        self._restore_console = win32.enable_application_mode()

        self.write("\x1b[?1049h")  # Enable alt screen
        self._enable_mouse_support()
        self.write("\x1b[?25h")  # Hide cursor
        self.write("\033[?1003h\n")
        self._enable_bracketed_paste()

        app = active_app.get()

        self._event_thread = win32.EventMonitor(
            loop, app, self._target, self.exit_event, self.process_event
        )
        self._event_thread.start()

    def disable_input(self) -> None:
        """Disable further input."""
        try:
            if not self.exit_event.is_set():
                self._disable_mouse_support()
                self.exit_event.set()
                if self._event_thread is not None:
                    self._event_thread.join()
                    self._event_thread = None
                self.exit_event.clear()
        except Exception as error:
            # TODO: log this
            pass

    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""
        self._disable_bracketed_paste()
        self.disable_input()
        if self._restore_console:
            self._restore_console()

        # Disable alt screen, show cursor
        self.write("\x1b[?1049l" + "\x1b[?25h")
        self.flush()
