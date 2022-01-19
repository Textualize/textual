from __future__ import annotations

import asyncio
from codecs import getincrementaldecoder
import msvcrt
import os
import selectors
import signal
import sys
from threading import Event, Thread
from typing import TYPE_CHECKING

from ..driver import Driver
from ..geometry import Size

from . import win32  #
from .. import events
from .. import log
from .._types import MessageTarget
from .._xterm_parser import XTermParser


if TYPE_CHECKING:
    from rich.console import Console


class WindowsDriver(Driver):
    """Powers display and input for Windows."""

    def __init__(self, console: "Console", target: "MessageTarget") -> None:
        super().__init__(console, target)
        self.in_fileno = sys.stdin.fileno()
        self.out_fileno = sys.stdout.fileno()

        self.exit_event = Event()
        self._key_thread: Thread | None = None

    def _get_terminal_size(self) -> tuple[int, int]:
        width, height = win32.get_terminal_size(self.out_fileno)
        return (width, height)

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

    def _disable_mouse_support(self) -> None:
        write = self.console.file.write
        write("\x1b[?1000l")  #
        write("\x1b[?1003l")  #
        write("\x1b[?1015l")
        write("\x1b[?1006l")
        self.console.file.flush()

    def start_application_mode(self) -> None:

        loop = asyncio.get_event_loop()

        filehandle = msvcrt.get_osfhandle(self.out_fileno)
        win32.enable_vt_mode(filehandle)

        self.console.set_alt_screen(True)
        self._enable_mouse_support()
        self.console.show_cursor(False)
        self.console.file.write("\033[?1003h\n")
        win32.setraw(msvcrt.get_osfhandle(self.in_fileno))

        self._key_thread = Thread(
            target=self.run_input_thread, args=(asyncio.get_event_loop(),)
        )

        width, height = win32.get_terminal_size(self.out_fileno)

        asyncio.run_coroutine_threadsafe(
            self._target.post_message(events.Resize(self._target, Size(width, height))),
            loop=loop,
        )
        log("starting key thread")
        self._key_thread.start()

    def disable_input(self) -> None:
        try:
            if not self.exit_event.is_set():
                self._disable_mouse_support()
                self.exit_event.set()
                if self._key_thread is not None:
                    self._key_thread.join()
        except Exception as error:
            # TODO: log this
            pass

    def stop_application_mode(self) -> None:
        self.disable_input()

        with self.console:
            self.console.set_alt_screen(False)
            self.console.show_cursor(True)

    def run_input_thread(self, loop) -> None:
        try:
            self._run_input_thread(loop)
        except Exception:
            pass  # TODO: log

    def _run_input_thread(self, loop) -> None:
        log("input thread")

        selector = selectors.DefaultSelector()
        selector.register(self.in_fileno, selectors.EVENT_READ)

        fileno = self.in_fileno

        def more_data() -> bool:
            """Check if there is more data to parse."""
            for key, events in selector.select(0.01):
                if events:
                    return True
            return False

        parser = XTermParser(self._target, more_data)

        utf8_decoder = getincrementaldecoder("utf-8")().decode
        decode = utf8_decoder
        read = os.read

        log("starting thread")
        try:
            while not self.exit_event.is_set():
                selector_events = selector.select(0.1)
                for _selector_key, mask in selector_events:
                    log(mask)
                    if mask | selectors.EVENT_READ:
                        unicode_data = decode(read(fileno, 1024))
                        log("ket", unicode_data)
                        for event in parser.feed(unicode_data):
                            self.process_event(event)
        except Exception as error:
            log(error)
        finally:
            selector.close()
