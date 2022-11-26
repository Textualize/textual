from __future__ import annotations

import os
from codecs import getincrementaldecoder
from contextlib import contextmanager
import selectors
import signal
import sys
import termios
import tty
from typing import Any, TYPE_CHECKING
from threading import Event, Thread
import anyio.abc
import anyio.from_thread

if TYPE_CHECKING:
    from rich.console import Console

import rich.repr

from .. import log
from ..driver import Driver
from ..geometry import Size
from .._types import MessageTarget
from .._xterm_parser import XTermParser
from .._profile import timer
from .. import events


@rich.repr.auto
class LinuxDriver(Driver):
    """Powers display and input for Linux / MacOS"""

    def __init__(
        self,
        console: "Console",
        target: "MessageTarget",
        task_group: anyio.abc.TaskGroup,
        *,
        debug: bool = False,
        size: tuple[int, int] | None = None,
    ) -> None:
        super().__init__(console, target, task_group, debug=debug, size=size)
        self.fileno = sys.stdin.fileno()
        self.attrs_before: list[Any] | None = None
        self.exit_event = Event()
        self._key_thread: Thread | None = None
        self._thread_portal: anyio.from_thread.BlockingPortal | None = None
        self._cancel_scopes = set()

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

    async def start_application_mode(self):
        def send_size_event():
            terminal_size = self._get_terminal_size()
            width, height = terminal_size
            textual_size = Size(width, height)
            event = events.Resize(self._target, textual_size, textual_size)
            self.send_event(event)

        async def signal_handler():
            with self._push_cancel_scope():
                with anyio.open_signal_receiver(signal.SIGWINCH) as receiver:
                    async for _ in receiver:
                        send_size_event()

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

        self._thread_portal = await self._start_thread_portal()

        self.console.show_cursor(False)
        self.console.file.write("\033[?1003h\n")
        self.console.file.flush()
        self._key_thread = Thread(
            target=self.run_input_thread, args=(self._thread_portal,)
        )
        send_size_event()
        self._key_thread.start()
        self._request_terminal_sync_mode_support()
        self._enable_bracketed_paste()

        self._task_group.start_soon(signal_handler)

    def _request_terminal_sync_mode_support(self):
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

    async def disable_input(self) -> None:
        try:
            if not self.exit_event.set():
                for scope in self._cancel_scopes:
                    scope.cancel()
                self._cancel_scopes.clear()
                self._disable_mouse_support()
                self.exit_event.set()
                if self._key_thread is not None:
                    self._key_thread.join()
                self.exit_event.clear()
                await self._thread_portal.stop()
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

    @contextmanager
    def _push_cancel_scope(self):
        with anyio.CancelScope() as cancel_scope:
            self._cancel_scopes.add(cancel_scope)
            try:
                yield
            finally:
                self._cancel_scopes.discard(cancel_scope)

    def run_input_thread(self, thread_portal: anyio.from_thread.BlockingPortal) -> None:
        try:
            self._run_input_thread(thread_portal)
        except Exception:
            pass  # TODO: log

    def _run_input_thread(
        self, thread_portal: anyio.from_thread.BlockingPortal
    ) -> None:

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
                # This causes spurious wakes and hurts battery life. It would
                # be better if this code were event driven.
                #
                # One way to do this would be anyio.wait_socket_readable, which
                # despite the documentation and function signature does seem to
                # work on arbitrary file descriptors on Linux. Another way
                # would be to use anyio.wrap_file, which does synchronous reads
                # in its own thread.
                selector_events = selector.select(0.1)
                for _selector_key, mask in selector_events:
                    if mask | EVENT_READ:
                        unicode_data = decode(read(fileno, 1024))
                        for event in feed(unicode_data):
                            thread_portal.call(self.process_event, event)
        except Exception as error:
            log(error)
        finally:
            with timer("selector.close"):
                selector.close()
