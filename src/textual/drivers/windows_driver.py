from __future__ import annotations

import asyncio
from ctypes import windll
from ctypes.wintypes import BOOL, DWORD, HANDLE
from codecs import getincrementaldecoder

import msvcrt
import os
import selectors
import signal
import sys
from threading import Event, Thread
from typing import List, Optional, TYPE_CHECKING

from ..driver import Driver
from ..geometry import Size

from . import win32  #
from .. import events
from .. import log
from .._types import MessageTarget
from .._xterm_parser import XTermParser


if TYPE_CHECKING:
    from rich.console import Console
    from textual.app import App

WAIT_TIMEOUT = 0x00000102


def wait_for_handles(handles: List[HANDLE], timeout: int = -1) -> Optional[HANDLE]:
    """
    Waits for multiple handles. (Similar to 'select') Returns the handle which is ready.
    Returns `None` on timeout.
    http://msdn.microsoft.com/en-us/library/windows/desktop/ms687025(v=vs.85).aspx
    Note that handles should be a list of `HANDLE` objects, not integers. See
    this comment in the patch by @quark-zju for the reason why:
        ''' Make sure HANDLE on Windows has a correct size
        Previously, the type of various HANDLEs are native Python integer
        types. The ctypes library will treat them as 4-byte integer when used
        in function arguments. On 64-bit Windows, HANDLE is 8-byte and usually
        a small integer. Depending on whether the extra 4 bytes are zero-ed out
        or not, things can happen to work, or break. '''
    This function returns either `None` or one of the given `HANDLE` objects.
    (The return value can be tested with the `is` operator.)
    """
    arrtype = HANDLE * len(handles)
    handle_array = arrtype(*handles)

    ret: int = windll.kernel32.WaitForMultipleObjects(
        len(handle_array), handle_array, BOOL(False), DWORD(timeout)
    )

    if ret == WAIT_TIMEOUT:
        return None
    else:
        return handles[ret]


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

        win32.enable_vt_mode(msvcrt.get_osfhandle(self.out_fileno))
        win32.setraw(msvcrt.get_osfhandle(self.in_fileno))

        self.console.set_alt_screen(True)
        self._enable_mouse_support()
        self.console.show_cursor(False)
        self.console.file.write("\033[?1003h\n")

        from .._context import active_app

        app = active_app.get()

        self._key_thread = Thread(
            target=self.run_input_thread, args=(asyncio.get_event_loop(), app)
        )

        width, height = win32.get_terminal_size(self.out_fileno)

        asyncio.run_coroutine_threadsafe(
            self._target.post_message(events.Resize(self._target, Size(width, height))),
            loop=loop,
        )

        from .._context import active_app

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

    def run_input_thread(self, loop, app: App) -> None:
        try:
            self._run_input_thread(loop, app)
        except Exception as error:
            app.log(error)

    def _run_input_thread(self, loop, app: App) -> None:
        app.log("input thread")

        parser = XTermParser(self._target, lambda: False)

        utf8_decoder = getincrementaldecoder("utf-8")().decode
        decode = utf8_decoder
        read = os.read

        input_handle = msvcrt.get_osfhandle(self.in_fileno)
        app.log("input_handle", input_handle)
        app.log("starting thread")
        try:
            while not self.exit_event.is_set():
                if wait_for_handles([input_handle], 100) is None:
                    continue
                unicode_data = decode(read(self.in_fileno, 1024))
                app.log("key", repr(unicode_data))
                for event in parser.feed(unicode_data):
                    self.process_event(event)
        except Exception as error:
            app.log(error)
        finally:
            app.log("input thread finished")
