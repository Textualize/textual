from __future__ import annotations

import asyncio
import os
from codecs import getincrementaldecoder
import selectors
import signal
import sys
import logging
import termios
from time import time
import tty
from typing import Any, TYPE_CHECKING
from threading import Event, Thread

if TYPE_CHECKING:
    from rich.console import Console


from . import events
from .driver import Driver
from ._types import MessageTarget
from ._xterm_parser import XTermParser


log = logging.getLogger("rich")


class LinuxDriver(Driver):
    def __init__(self, console: "Console", target: "MessageTarget") -> None:
        super().__init__(console, target)
        self.fileno = sys.stdin.fileno()
        self.attrs_before: list[Any] | None = None
        self.exit_event = Event()
        self._key_thread: Thread | None = None

    def _get_terminal_size(self) -> tuple[int, int]:
        width: int | None = 80
        height: int | None = 25
        try:
            width, height = os.get_terminal_size(sys.stdin.fileno())
        except (AttributeError, ValueError, OSError):
            try:
                width, height = os.get_terminal_size(sys.stdout.fileno())
            except (AttributeError, ValueError, OSError):
                pass
        width = width or 80
        height = height or 25
        return width, height

    def _enable_mouse_support(self) -> None:
        write = self.console.file.write
        write("\x1b[?1000h")

        write("\x1b[?1015h")
        write("\x1b[?1006h")

        # write("\x1b[?1007h")
        self.console.file.flush()

        # Note: E.g. lxterminal understands 1000h, but not the urxvt or sgr
        #       extensions.

    def _disable_mouse_support(self) -> None:
        write = self.console.file.write
        write("\x1b[?1000l")
        write("\x1b[?1015l")
        write("\x1b[?1006l")
        self.console.file.flush()

    def start_application_mode(self):

        loop = asyncio.get_event_loop()

        def on_terminal_resize(signum, stack) -> None:
            terminal_size = self._get_terminal_size()
            width, height = terminal_size
            event = events.Resize(self._target, width, height)
            self.console.size = terminal_size
            asyncio.run_coroutine_threadsafe(
                self._target.post_message(event),
                loop=loop,
            )

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

        self._key_thread = Thread(
            target=self.run_input_thread, args=(asyncio.get_event_loop(),)
        )
        width, height = self.console.size = self._get_terminal_size()
        asyncio.run_coroutine_threadsafe(
            self._target.post_message(events.Resize(self._target, width, height)),
            loop=loop,
        )
        self._key_thread.start()

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
        except Exception:
            log.exception("error in disable_input")

    def stop_application_mode(self) -> None:
        log.debug("stop_application_mode()")

        self.disable_input()

        if self.attrs_before is not None:
            try:
                termios.tcsetattr(self.fileno, termios.TCSANOW, self.attrs_before)
            except termios.error:
                pass

        self.console.set_alt_screen(False)
        self.console.show_cursor(True)

    def run_input_thread(self, loop) -> None:
        try:
            self._run_input_thread(loop)
        except Exception:
            log.exception("error running input thread")

    def _run_input_thread(self, loop) -> None:
        def send_event(event: events.Event) -> None:
            asyncio.run_coroutine_threadsafe(
                self._target.post_message(event),
                loop=loop,
            )

        selector = selectors.DefaultSelector()
        selector.register(self.fileno, selectors.EVENT_READ)

        fileno = self.fileno

        def more_data() -> bool:
            """Check if there is more data to parse."""
            for key, events in selector.select(0.1):
                if events:
                    return True
            return False

        parser = XTermParser(self._target, more_data)

        utf8_decoder = getincrementaldecoder("utf-8")().decode
        decode = utf8_decoder
        read = os.read

        mouse_down_time = time()

        log.debug("started key thread")
        try:
            while not self.exit_event.is_set():
                selector_events = selector.select(0.1)
                for _selector_key, mask in selector_events:
                    if mask | selectors.EVENT_READ:
                        unicode_data = decode(read(fileno, 1024))
                        for event in parser.feed(unicode_data):
                            self.process_event(event)
        except Exception:
            log.exception("error running key thread")
        finally:
            selector.close()


if __name__ == "__main__":
    from time import sleep
    from rich.console import Console
    from . import events

    console = Console()

    from .app import App

    class MyApp(App):
        async def on_startup(self, event: events.Startup) -> None:
            self.set_timer(5, callback=self.close_messages)

    MyApp.run()
