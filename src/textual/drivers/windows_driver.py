from __future__ import annotations

import asyncio
import sys
from threading import Event, Thread
from typing import TYPE_CHECKING, Callable

from .._context import active_app
from .._types import MessageTarget
from ..driver import Driver
from . import win32

if TYPE_CHECKING:
    from rich.console import Console


class WindowsDriver(Driver):
    """Powers display and input for Windows."""

    def __init__(
        self,
        console: "Console",
        target: "MessageTarget",
        *,
        debug: bool = False,
        size: tuple[int, int] | None = None,
    ) -> None:
        super().__init__(console, target, debug=debug, size=size)
        self.in_fileno = sys.stdin.fileno()
        self.out_fileno = sys.stdout.fileno()

        self.exit_event = Event()
        self._event_thread: Thread | None = None
        self._restore_console: Callable[[], None] | None = None

    def _enable_mouse_support(self) -> None:
        write = self.console.file.write
        write("\x1b[?1000h")  # SET_VT200_MOUSE
        write("\x1b[?1003h")  # SET_ANY_EVENT_MOUSE
        write("\x1b[?1015h")  # SET_VT200_HIGHLIGHT_MOUSE
        write("\x1b[?1006h")  # SET_SGR_EXT_MODE_MOUSE
        self.console.file.flush()

    def _disable_mouse_support(self) -> None:
        write = self.console.file.write
        write("\x1b[?1000l")
        write("\x1b[?1003l")
        write("\x1b[?1015l")
        write("\x1b[?1006l")
        self.console.file.flush()

    def _enable_bracketed_paste(self) -> None:
        """Enable bracketed paste mode."""
        self.console.file.write("\x1b[?2004h")

    def _disable_bracketed_paste(self) -> None:
        """Disable bracketed paste mode."""
        self.console.file.write("\x1b[?2004l")

    def start_application_mode(self) -> None:

        loop = asyncio.get_running_loop()

        self._restore_console = win32.enable_application_mode()

        self.console.set_alt_screen(True)
        self._enable_mouse_support()
        self.console.show_cursor(False)
        self.console.file.write("\033[?1003h\n")
        self._enable_bracketed_paste()

        app = active_app.get()

        self._event_thread = win32.EventMonitor(
            loop, app, self._target, self.exit_event, self.process_event
        )
        self._event_thread.start()

    def disable_input(self) -> None:
        try:
            if not self.exit_event.is_set():
                self._disable_mouse_support()
                self.exit_event.set()
                if self._event_thread is not None:
                    self._event_thread.join()
                    self._event_thread = None
        except Exception as error:
            # TODO: log this
            pass

    def stop_application_mode(self) -> None:
        self._disable_bracketed_paste()
        self.disable_input()
        if self._restore_console:
            self._restore_console()
        with self.console:
            self.console.set_alt_screen(False)
            self.console.show_cursor(True)
