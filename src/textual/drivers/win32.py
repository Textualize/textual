from __future__ import annotations

import ctypes
import msvcrt
import sys
import threading
from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from ctypes import Structure, Union, byref, wintypes
from ctypes.wintypes import BOOL, CHAR, DWORD, HANDLE, SHORT, UINT, WCHAR, WORD
from typing import IO, TYPE_CHECKING, Callable, List, Optional

from textual import constants
from textual._xterm_parser import XTermParser
from textual.events import Event, Resize
from textual.geometry import Size

if TYPE_CHECKING:
    from textual.app import App

KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore

# Console input modes
ENABLE_ECHO_INPUT = 0x0004
ENABLE_EXTENDED_FLAGS = 0x0080
ENABLE_INSERT_MODE = 0x0020
ENABLE_LINE_INPUT = 0x0002
ENABLE_MOUSE_INPUT = 0x0010
ENABLE_PROCESSED_INPUT = 0x0001
ENABLE_QUICK_EDIT_MODE = 0x0040
ENABLE_WINDOW_INPUT = 0x0008
ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200

# Console output modes
ENABLE_PROCESSED_OUTPUT = 0x0001
ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
DISABLE_NEWLINE_AUTO_RETURN = 0x0008
ENABLE_LVB_GRID_WORLDWIDE = 0x0010

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11

WAIT_TIMEOUT = 0x00000102

GetStdHandle = KERNEL32.GetStdHandle
GetStdHandle.argtypes = [wintypes.DWORD]
GetStdHandle.restype = wintypes.HANDLE


class COORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/coord-str"""

    _fields_ = [
        ("X", SHORT),
        ("Y", SHORT),
    ]


class uChar(Union):
    """https://docs.microsoft.com/en-us/windows/console/key-event-record-str"""

    _fields_ = [
        ("AsciiChar", CHAR),
        ("UnicodeChar", WCHAR),
    ]


class KEY_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/key-event-record-str"""

    _fields_ = [
        ("bKeyDown", BOOL),
        ("wRepeatCount", WORD),
        ("wVirtualKeyCode", WORD),
        ("wVirtualScanCode", WORD),
        ("uChar", uChar),
        ("dwControlKeyState", DWORD),
    ]


class MOUSE_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/mouse-event-record-str"""

    _fields_ = [
        ("dwMousePosition", COORD),
        ("dwButtonState", DWORD),
        ("dwControlKeyState", DWORD),
        ("dwEventFlags", DWORD),
    ]


class WINDOW_BUFFER_SIZE_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/window-buffer-size-record-str"""

    _fields_ = [("dwSize", COORD)]


class MENU_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/menu-event-record-str"""

    _fields_ = [("dwCommandId", UINT)]


class FOCUS_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/focus-event-record-str"""

    _fields_ = [("bSetFocus", BOOL)]


class InputEvent(Union):
    """https://docs.microsoft.com/en-us/windows/console/input-record-str"""

    _fields_ = [
        ("KeyEvent", KEY_EVENT_RECORD),
        ("MouseEvent", MOUSE_EVENT_RECORD),
        ("WindowBufferSizeEvent", WINDOW_BUFFER_SIZE_RECORD),
        ("MenuEvent", MENU_EVENT_RECORD),
        ("FocusEvent", FOCUS_EVENT_RECORD),
    ]


class INPUT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/input-record-str"""

    _fields_ = [("EventType", wintypes.WORD), ("Event", InputEvent)]


def set_console_mode(file: IO, mode: int) -> bool:
    """Set the console mode for a given file (stdout or stdin).

    Args:
        file: A file like object.
        mode: New mode.

    Returns:
        True on success, otherwise False.
    """
    windows_filehandle = msvcrt.get_osfhandle(file.fileno())  # type: ignore
    success = KERNEL32.SetConsoleMode(windows_filehandle, mode)
    return success


def get_console_mode(file: IO) -> int:
    """Get the console mode for a given file (stdout or stdin)

    Args:
        file: A file-like object.

    Returns:
        The current console mode.
    """
    windows_filehandle = msvcrt.get_osfhandle(file.fileno())  # type: ignore
    mode = wintypes.DWORD()
    KERNEL32.GetConsoleMode(windows_filehandle, ctypes.byref(mode))
    return mode.value


def enable_application_mode() -> Callable[[], None]:
    """Enable application mode.

    Returns:
        A callable that will restore terminal to previous state.
    """

    terminal_in = sys.__stdin__
    terminal_out = sys.__stdout__

    current_console_mode_in = get_console_mode(terminal_in)
    current_console_mode_out = get_console_mode(terminal_out)

    def restore() -> None:
        """Restore console mode to previous settings"""
        set_console_mode(terminal_in, current_console_mode_in)
        set_console_mode(terminal_out, current_console_mode_out)

    set_console_mode(
        terminal_out, current_console_mode_out | ENABLE_VIRTUAL_TERMINAL_PROCESSING
    )
    set_console_mode(terminal_in, ENABLE_VIRTUAL_TERMINAL_INPUT)
    return restore


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

    ret: int = KERNEL32.WaitForMultipleObjects(
        len(handle_array), handle_array, BOOL(False), DWORD(timeout)
    )

    if ret == WAIT_TIMEOUT:
        return None
    else:
        return handles[ret]


class EventMonitor(threading.Thread):
    """A thread to send key / window events to Textual loop."""

    def __init__(
        self,
        loop: AbstractEventLoop,
        app: App,
        exit_event: threading.Event,
        process_event: Callable[[Event], None],
    ) -> None:
        self.loop = loop
        self.app = app
        self.exit_event = exit_event
        self.process_event = process_event
        super().__init__(name="textual-input")

    def run(self) -> None:
        exit_requested = self.exit_event.is_set
        parser = XTermParser(debug=constants.DEBUG)

        try:
            read_count = wintypes.DWORD(0)
            hIn = GetStdHandle(STD_INPUT_HANDLE)

            MAX_EVENTS = 1024
            KEY_EVENT = 0x0001
            WINDOW_BUFFER_SIZE_EVENT = 0x0004

            arrtype = INPUT_RECORD * MAX_EVENTS
            input_records = arrtype()
            ReadConsoleInputW = KERNEL32.ReadConsoleInputW
            keys: List[str] = []
            append_key = keys.append

            while not exit_requested():

                for event in parser.tick():
                    self.process_event(event)

                # Wait for new events
                if wait_for_handles([hIn], 100) is None:
                    # No new events
                    continue

                # Get new events
                ReadConsoleInputW(
                    hIn, byref(input_records), MAX_EVENTS, byref(read_count)
                )
                read_input_records = input_records[: read_count.value]

                del keys[:]
                new_size: Optional[tuple[int, int]] = None

                for input_record in read_input_records:
                    event_type = input_record.EventType

                    if event_type == KEY_EVENT:
                        # Key event, store unicode char in keys list
                        key_event = input_record.Event.KeyEvent
                        key = key_event.uChar.UnicodeChar
                        if key_event.bKeyDown:
                            if (
                                key_event.dwControlKeyState
                                and key_event.wVirtualKeyCode == 0
                            ):
                                continue
                            append_key(key)
                    elif event_type == WINDOW_BUFFER_SIZE_EVENT:
                        # Window size changed, store size
                        size = input_record.Event.WindowBufferSizeEvent.dwSize
                        new_size = (size.X, size.Y)

                if keys:
                    # Process keys
                    #
                    # https://github.com/Textualize/textual/issues/3178 has
                    # the context for the encode/decode here.
                    for event in parser.feed(
                        "".join(keys).encode("utf-16", "surrogatepass").decode("utf-16")
                    ):
                        self.process_event(event)
                if new_size is not None:
                    # Process changed size
                    self.on_size_change(*new_size)

        except Exception as error:
            self.app.log.error("EVENT MONITOR ERROR", error)

    def on_size_change(self, width: int, height: int) -> None:
        """Called when terminal size changes."""
        size = Size(width, height)
        event = Resize(size, size)
        run_coroutine_threadsafe(self.app._post_message(event), loop=self.loop)
