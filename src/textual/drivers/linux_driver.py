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

if TYPE_CHECKING:
    from rich.console import Console

import rich.repr

from .. import events, log
from .._profile import timer
from .._types import MessageTarget
from .._xterm_parser import XTermParser
from ..driver import Driver
from ..geometry import Size


@rich.repr.auto
class LinuxDriver(Driver):
    """Powers display and input for Linux / MacOS"""

    def __init__(
        self,
        console: "Console",
        target: "MessageTarget",
        *,
        debug: bool = False,
        size: tuple[int, int] | None = None,
    ) -> None:
        super().__init__(console, target, debug=debug, size=size)
        self.fileno = sys.stdin.fileno()
        self.attrs_before: list[Any] | None = None
        self.exit_event = Event()
        self._key_thread: Thread | None = None

    def __rich_repr__(self) -> rich.repr.Result:
        yield "debug", self._debug

    def _get_terminal_size(self) -> tuple[int, int]:
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
        write = self.console.file.write
        write("\x1b[?1000h")  # SET_VT200_MOUSE
        write("\x1b[?1003h")  # SET_ANY_EVENT_MOUSE
        write("\x1b[?1015h")  # SET_VT200_HIGHLIGHT_MOUSE
        write("\x1b[?1006h")  # SET_SGR_EXT_MODE_MOUSE

        # write("\x1b[?1007h")
        self.console.file.flush()

        # Note: E.g. lxterminal understands 1000h, but not the urxvt or sgr
        #       extensions.

    def _enable_bracketed_paste(self) -> None:
        """Enable bracketed paste mode."""
        self.console.file.write("\x1b[?2004h")

    def _disable_bracketed_paste(self) -> None:
        """Disable bracketed paste mode."""
        self.console.file.write("\x1b[?2004l")

    def _disable_mouse_support(self) -> None:
        write = self.console.file.write
        write("\x1b[?1000l")  #
        write("\x1b[?1003l")  #
        write("\x1b[?1015l")
        write("\x1b[?1006l")
        self.console.file.flush()

    def start_application_mode(self):
        loop = asyncio.get_running_loop()

        def send_size_event():
            terminal_size = self._get_terminal_size()
            width, height = terminal_size
            textual_size = Size(width, height)
            event = events.Resize(self._target, textual_size, textual_size)
            asyncio.run_coroutine_threadsafe(
                self._target.post_message(event),
                loop=loop,
            )

        def on_terminal_resize(signum, stack) -> None:
            send_size_event()

        signal.signal(signal.SIGWINCH, on_terminal_resize)

        self.console.set_alt_screen(True)
        self._enable_mouse_support()
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

        self.console.show_cursor(False)
        self.console.file.write("\033[?1003h\n")
        self.console.file.flush()
        self._key_thread = Thread(target=self.run_input_thread, args=(loop,))
        send_size_event()
        self._key_thread.start()
        self._request_terminal_sync_mode_support()
        self._enable_bracketed_paste()

    def _request_terminal_sync_mode_support(self) -> None:
        """Writes an escape sequence to query the terminal support for the sync protocol."""
        # Terminals should ignore this sequence if not supported.
        # Apple terminal doesn't, and writes a single 'p' in to the terminal,
        # so we will make a special case for Apple terminal (which doesn't support sync anyway).
        if self.console._environ.get("TERM_PROGRAM", "") != "Apple_Terminal":
            self.console.file.write("\033[?2026$p")
            self.console.file.flush()

    @classmethod
    def _patch_lflag(cls, attrs: int) -> int:
        return attrs & ~(termios.ECHO | termios.ICANON | termios.IEXTEN | termios.ISIG)

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
        try:
            if not self.exit_event.is_set():
                signal.signal(signal.SIGWINCH, signal.SIG_DFL)
                self._disable_mouse_support()
                self.exit_event.set()
                if self._key_thread is not None:
                    self._key_thread.join()
                self.exit_event.clear()
                termios.tcflush(self.fileno, termios.TCIFLUSH)
        except Exception as error:
            # TODO: log this
            pass

    def stop_application_mode(self) -> None:
        self._disable_bracketed_paste()
        self.disable_input()

        if self.attrs_before is not None:
            try:
                termios.tcsetattr(self.fileno, termios.TCSANOW, self.attrs_before)
            except termios.error:
                pass

        with self.console:
            self.console.set_alt_screen(False)
            self.console.show_cursor(True)

    def run_input_thread(self, loop) -> None:
        try:
            self._run_input_thread(loop)
        except Exception:
            pass  # TODO: log

    def _run_input_thread(self, loop) -> None:
        selector = selectors.DefaultSelector()
        selector.register(self.fileno, selectors.EVENT_READ)

        fileno = self.fileno

        def more_data() -> bool:
            """Check if there is more data to parse."""
            for key, events in selector.select(0.01):
                if events:
                    return True
            return False

        parser = XTermParser(self._target, more_data, self._debug)
        feed = parser.feed

        utf8_decoder = getincrementaldecoder("utf-8")().decode
        decode = utf8_decoder
        read = os.read
        EVENT_READ = selectors.EVENT_READ

        try:
            while not self.exit_event.is_set():
                selector_events = selector.select(0.1)
                for _selector_key, mask in selector_events:
                    if mask | EVENT_READ:
                        unicode_data = decode(read(fileno, 1024))
                        for event in feed(unicode_data):
                            self.process_event(event)
        except Exception as error:
            log(error)
        finally:
            selector.close()
