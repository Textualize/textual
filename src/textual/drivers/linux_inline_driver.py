from __future__ import annotations

import asyncio
import os
import selectors
import signal
import sys
import termios
import tty
from codecs import getincrementaldecoder
from threading import Event, Thread
from typing import TYPE_CHECKING, Any

import rich.repr

from textual import events
from textual._loop import loop_last
from textual._parser import ParseError
from textual._xterm_parser import XTermParser
from textual.driver import Driver
from textual.geometry import Size

if TYPE_CHECKING:
    from textual.app import App


@rich.repr.auto(angular=True)
class LinuxInlineDriver(Driver):
    def __init__(
        self,
        app: App,
        *,
        debug: bool = False,
        mouse: bool = True,
        size: tuple[int, int] | None = None,
    ):
        super().__init__(app, debug=debug, mouse=mouse, size=size)
        self._file = sys.__stderr__
        self.fileno = sys.__stdin__.fileno()
        self.attrs_before: list[Any] | None = None
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

    def _enable_mouse_support(self) -> None:
        """Enable reporting of mouse events."""
        if not self._mouse:
            return
        write = self.write
        write("\x1b[?1000h")  # SET_VT200_MOUSE
        write("\x1b[?1003h")  # SET_ANY_EVENT_MOUSE
        write("\x1b[?1015h")  # SET_VT200_HIGHLIGHT_MOUSE
        write("\x1b[?1006h")  # SET_SGR_EXT_MODE_MOUSE

        # write("\x1b[?1007h")
        self.flush()

    def _disable_mouse_support(self) -> None:
        """Disable reporting of mouse events."""
        if not self._mouse:
            return
        write = self.write
        write("\x1b[?1000l")  #
        write("\x1b[?1003l")  #
        write("\x1b[?1015l")
        write("\x1b[?1006l")
        self.flush()

    def write(self, data: str) -> None:
        self._file.write(data)

    def _run_input_thread(self) -> None:
        """
        Key thread target that wraps run_input_thread() to die gracefully if it raises
        an exception
        """
        try:
            self.run_input_thread()
        except BaseException:
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

        parser = XTermParser(self._debug)
        feed = parser.feed
        tick = parser.tick

        utf8_decoder = getincrementaldecoder("utf-8")().decode
        decode = utf8_decoder
        read = os.read

        def process_selector_events(
            selector_events: list[tuple[selectors.SelectorKey, int]],
            final: bool = False,
        ) -> None:
            """Process events from selector.

            Args:
                selector_events: List of selector events.
                final: True if this is the last call.

            """
            for last, (_selector_key, mask) in loop_last(selector_events):
                if mask & EVENT_READ:
                    unicode_data = decode(read(fileno, 1024 * 4), final=final and last)
                    if not unicode_data:
                        # This can occur if the stdin is piped
                        break
                    for event in feed(unicode_data):
                        if isinstance(event, events.CursorPosition):
                            self.cursor_origin = (event.x, event.y)
                        else:
                            self.process_message(event)
            for event in tick():
                if isinstance(event, events.CursorPosition):
                    self.cursor_origin = (event.x, event.y)
                else:
                    self.process_message(event)

        try:
            while not self.exit_event.is_set():
                process_selector_events(selector.select(0.1))
            selector.unregister(self.fileno)
            process_selector_events(selector.select(0.1), final=True)

        finally:
            selector.close()
            try:
                for event in feed(""):
                    pass
            except ParseError:
                pass

    def start_application_mode(self) -> None:
        loop = asyncio.get_running_loop()

        def send_size_event(clear: bool = False) -> None:
            """Send the resize event, optionally clearing the screen.

            Args:
                clear: Clear the screen.
            """
            terminal_size = self._get_terminal_size()
            width, height = terminal_size
            textual_size = Size(width, height)
            event = events.Resize(textual_size, textual_size)

            async def update_size() -> None:
                """Update the screen size."""
                if clear:
                    self.write("\x1b[2J")
                await self._app._post_message(event)

            asyncio.run_coroutine_threadsafe(
                update_size(),
                loop=loop,
            )

        def on_terminal_resize(signum, stack) -> None:
            send_size_event(clear=True)

        signal.signal(signal.SIGWINCH, on_terminal_resize)

        self.write("\x1b[?25l")  # Hide cursor
        self.write("\033[?1004h")  # Enable FocusIn/FocusOut.
        self.write("\x1b[>1u")  # https://sw.kovidgoyal.net/kitty/keyboard-protocol/
        self.flush()

        self._enable_mouse_support()
        self.write("\n" * self._app.INLINE_PADDING)
        self.flush()
        try:
            self.attrs_before = termios.tcgetattr(self.fileno)
        except termios.error:
            # Ignore attribute errors.
            self.attrs_before = None

        try:
            newattr = termios.tcgetattr(self.fileno)
        except termios.error:
            pass
        else:
            newattr[tty.LFLAG] = self._patch_lflag(newattr[tty.LFLAG])
            newattr[tty.IFLAG] = self._patch_iflag(newattr[tty.IFLAG])

            # VMIN defines the number of characters read at a time in
            # non-canonical mode. It seems to default to 1 on Linux, but on
            # Solaris and derived operating systems it defaults to 4. (This is
            # because the VMIN slot is the same as the VEOF slot, which
            # defaults to ASCII EOT = Ctrl-D = 4.)
            newattr[tty.CC][termios.VMIN] = 1

            termios.tcsetattr(self.fileno, termios.TCSANOW, newattr)

        self._key_thread = Thread(target=self._run_input_thread, name="textual-input")
        send_size_event()
        self._key_thread.start()
        self._request_terminal_sync_mode_support()
        self._enable_bracketed_paste()

    def _request_terminal_sync_mode_support(self) -> None:
        """Writes an escape sequence to query the terminal support for the sync protocol."""
        # Terminals should ignore this sequence if not supported.
        # Apple terminal doesn't, and writes a single 'p' into the terminal,
        # so we will make a special case for Apple terminal (which doesn't support sync anyway).
        if os.environ.get("TERM_PROGRAM", "") != "Apple_Terminal":
            self.write("\033[?2026$p")
            self.flush()

    @classmethod
    def _patch_lflag(cls, attrs: int) -> int:
        """Patch termios lflag.

        Args:
            attributes: New set attributes.

        Returns:
            New lflag.

        """
        # if TEXTUAL_ALLOW_SIGNALS env var is set, then allow Ctrl+C to send signals
        ISIG = 0 if os.environ.get("TEXTUAL_ALLOW_SIGNALS") else termios.ISIG

        return attrs & ~(termios.ECHO | termios.ICANON | termios.IEXTEN | ISIG)

    @classmethod
    def _patch_iflag(cls, attrs: int) -> int:
        return attrs & ~(
            # Disable XON/XOFF flow control on output and input.
            # (Don't capture Ctrl-S and Ctrl-Q.)
            # Like executing: "stty -ixon."
            termios.IXON
            | termios.IXOFF
            |
            # Don't translate carriage return into newline on input.
            termios.ICRNL
            | termios.INLCR
            | termios.IGNCR
        )

    def disable_input(self) -> None:
        """Disable further input."""
        try:
            if not self.exit_event.is_set():
                signal.signal(signal.SIGWINCH, signal.SIG_DFL)
                self._disable_mouse_support()
                self.exit_event.set()
                if self._key_thread is not None:
                    self._key_thread.join()
                self.exit_event.clear()
                try:
                    termios.tcflush(self.fileno, termios.TCIFLUSH)
                except termios.error:
                    pass

        except Exception as error:
            # TODO: log this
            pass

    def flush(self):
        """Flush any buffered data."""
        self._file.flush()

    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""
        self._disable_bracketed_paste()
        self.disable_input()
        self.write("\x1b[<u")  # Disable kitty protocol
        self.write("\x1b[J")

        if self.attrs_before is not None:
            try:
                termios.tcsetattr(self.fileno, termios.TCSANOW, self.attrs_before)
            except termios.error:
                pass

            self.write("\x1b[?25h")  # Show cursor
            self.write("\033[?1004l")  # Disable FocusIn/FocusOut.

        self.flush()
