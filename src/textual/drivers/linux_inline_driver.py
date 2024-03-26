from __future__ import annotations

import asyncio
import os
import selectors
import signal
import sys
from codecs import getincrementaldecoder
from threading import Event, Thread
from typing import TYPE_CHECKING

import rich.repr

from .. import events
from .._xterm_parser import XTermParser
from ..driver import Driver
from ..geometry import Size

if TYPE_CHECKING:
    from ..app import App


@rich.repr.auto(angular=True)
class LinuxInlineDriver(Driver):

    def __init__(
        self,
        app: App,
        *,
        debug: bool = False,
        size: tuple[int, int] | None = None,
    ):
        super().__init__(app, debug=debug, size=size)
        self._file = sys.__stderr__
        self.fileno = sys.__stdin__.fileno()
        self.exit_event = Event()

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._app

    @property
    def is_inline(self) -> bool:
        return True

    def _enable_bracketed_paste(self) -> None:
        """Enable bracketed paste mode."""
        self.write("\x1b[?2004h")

    def _disable_bracketed_paste(self) -> None:
        """Disable bracketed paste mode."""
        self.write("\x1b[?2004l")

    def _get_terminal_size(self) -> tuple[int, int]:
        """Detect the terminal size.

        Returns:
            The size of the terminal as a tuple of (WIDTH, HEIGHT).
        """
        width: int | None = 80
        height: int | None = 25
        import shutil

        try:
            width, height = shutil.get_terminal_size()
        except (AttributeError, ValueError, OSError):
            try:
                width, height = shutil.get_terminal_size()
            except (AttributeError, ValueError, OSError):
                pass
        width = width or 80
        height = height or 25
        return width, height

    def write(self, data: str) -> None:
        self._file.write(data)

    def _run_input_thread(self) -> None:
        """
        Key thread target that wraps run_input_thread() to die gracefully if it raises
        an exception
        """
        try:
            self.run_input_thread()
        except BaseException as error:
            import rich.traceback

            self._app.call_later(
                self._app.panic,
                rich.traceback.Traceback(),
            )

    def run_input_thread(self) -> None:
        """Wait for input and dispatch events."""
        selector = selectors.SelectSelector()
        selector.register(self.fileno, selectors.EVENT_READ)

        fileno = self.fileno
        EVENT_READ = selectors.EVENT_READ

        def more_data() -> bool:
            """Check if there is more data to parse."""

            for _key, events in selector.select(0.01):
                if events & EVENT_READ:
                    return True
            return False

        parser = XTermParser(more_data, self._debug)
        feed = parser.feed

        utf8_decoder = getincrementaldecoder("utf-8")().decode
        decode = utf8_decoder
        read = os.read

        try:
            while not self.exit_event.is_set():
                selector_events = selector.select(0.1)
                for _selector_key, mask in selector_events:
                    if mask & EVENT_READ:
                        unicode_data = decode(
                            read(fileno, 1024), final=self.exit_event.is_set()
                        )
                        for event in feed(unicode_data):
                            self.process_event(event)
        finally:
            selector.close()

    def start_application_mode(self) -> None:

        loop = asyncio.get_running_loop()

        def send_size_event():
            terminal_size = self._get_terminal_size()
            width, height = terminal_size
            textual_size = Size(width, height)
            event = events.Resize(textual_size, textual_size)
            asyncio.run_coroutine_threadsafe(
                self._app._post_message(event),
                loop=loop,
            )

            def on_terminal_resize(signum, stack) -> None:
                send_size_event()

            signal.signal(signal.SIGWINCH, on_terminal_resize)

        self.write("\x1b[?25l")  # Hide cursor
        self.write("\033[?1004h\n")  # Enable FocusIn/FocusOut.

        self._key_thread = Thread(target=self._run_input_thread)
        send_size_event()
        self._key_thread.start()

    def disable_input(self) -> None:
        """Disable further input."""
        try:
            if not self.exit_event.is_set():
                signal.signal(signal.SIGWINCH, signal.SIG_DFL)
                self.exit_event.set()
                if self._key_thread is not None:
                    self._key_thread.join()
                self.exit_event.clear()

        except Exception as error:
            # TODO: log this
            pass

    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""
        self._disable_bracketed_paste()
        self.disable_input()

        # Alt screen false, show cursor
        self.write("\x1b[?25h")
        self.write("\033[?1004l\n")  # Disable FocusIn/FocusOut.
        self.flush()
