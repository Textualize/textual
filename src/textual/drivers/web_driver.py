"""

The Remote driver uses the following packet structure.

1 byte for packet type. "D" for data, "M" for meta.
4 byte little endian integer for the size of the payload.
Arbitrary payload.


"""

from __future__ import annotations

import asyncio
import json
import os
import platform
import signal
import sys
from codecs import getincrementaldecoder
from functools import partial
from threading import Event, Thread

from .. import events, log, messages
from .._xterm_parser import XTermParser
from ..app import App
from ..driver import Driver
from ..geometry import Size
from ._byte_stream import ByteStream
from ._input_reader import InputReader

WINDOWS = platform.system() == "Windows"


class _ExitInput(Exception):
    """Internal exception to force exit of input loop."""


class WebDriver(Driver):
    """A headless driver that may be run remotely."""

    def __init__(
        self,
        app: App,
        *,
        debug: bool = False,
        mouse: bool = True,
        size: tuple[int, int] | None = None,
    ):
        if size is None:
            try:
                width = int(os.environ.get("COLUMNS", 80))
                height = int(os.environ.get("ROWS", 24))
            except ValueError:
                pass
            else:
                size = width, height
        super().__init__(app, debug=debug, mouse=mouse, size=size)
        self.stdout = sys.__stdout__
        self.fileno = sys.__stdout__.fileno()
        self._write = partial(os.write, self.fileno)
        self.exit_event = Event()
        self._key_thread: Thread = Thread(target=self.run_input_thread)
        self._input_reader = InputReader()

    def write(self, data: str) -> None:
        """Write data to the output device.

        Args:
            data: Raw data.
        """

        data_bytes = data.encode("utf-8")
        self._write(b"D%s%s" % (len(data_bytes).to_bytes(4, "big"), data_bytes))

    def write_meta(self, data: dict[str, object]) -> None:
        """Write meta to the controlling process (i.e. textual-web)

        Args:
            data: Meta dict.
        """
        meta_bytes = json.dumps(data).encode("utf-8", errors="ignore")
        self._write(b"M%s%s" % (len(meta_bytes).to_bytes(4, "big"), meta_bytes))

    def flush(self) -> None:
        pass

    def _enable_mouse_support(self) -> None:
        """Enable reporting of mouse events."""
        write = self.write
        write("\x1b[?1000h")  # SET_VT200_MOUSE
        write("\x1b[?1003h")  # SET_ANY_EVENT_MOUSE
        write("\x1b[?1015h")  # SET_VT200_HIGHLIGHT_MOUSE
        write("\x1b[?1006h")  # SET_SGR_EXT_MODE_MOUSE

    def _enable_bracketed_paste(self) -> None:
        """Enable bracketed paste mode."""
        self.write("\x1b[?2004h")

    def _disable_bracketed_paste(self) -> None:
        """Disable bracketed paste mode."""
        self.write("\x1b[?2004l")

    def _disable_mouse_support(self) -> None:
        """Disable reporting of mouse events."""
        write = self.write
        write("\x1b[?1000l")  #
        write("\x1b[?1003l")  #
        write("\x1b[?1015l")
        write("\x1b[?1006l")

    def _request_terminal_sync_mode_support(self) -> None:
        """Writes an escape sequence to query the terminal support for the sync protocol."""
        self.write("\033[?2026$p")

    def start_application_mode(self) -> None:
        """Start application mode."""

        loop = asyncio.get_running_loop()

        def do_exit() -> None:
            """Callback to force exit."""
            asyncio.run_coroutine_threadsafe(
                self._app._post_message(messages.ExitApp()), loop=loop
            )

        if not WINDOWS:
            for _signal in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(_signal, do_exit)

        self._write(b"__GANGLION__\n")

        self.write("\x1b[?1049h")  # Alt screen
        self._enable_mouse_support()

        self.write("\x1b[?25l")  # Hide cursor
        self.write("\033[?1003h")

        size = Size(80, 24) if self._size is None else Size(*self._size)
        event = events.Resize(size, size)
        asyncio.run_coroutine_threadsafe(
            self._app._post_message(event),
            loop=loop,
        )

        self._request_terminal_sync_mode_support()
        self._enable_bracketed_paste()
        self.flush()
        self._key_thread.start()
        self._app.post_message(events.AppBlur())

    def disable_input(self) -> None:
        """Disable further input."""

    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""
        self.exit_event.set()
        self._input_reader.close()
        self.write_meta({"type": "exit"})

    def run_input_thread(self) -> None:
        """Wait for input and dispatch events."""
        input_reader = self._input_reader
        parser = XTermParser(input_reader.more_data, debug=self._debug)
        utf8_decoder = getincrementaldecoder("utf-8")().decode
        decode = utf8_decoder
        # The server sends us a stream of bytes, which contains the equivalent of stdin, plus
        # in band data packets.
        byte_stream = ByteStream()
        try:
            for data in input_reader:
                for packet_type, payload in byte_stream.feed(data):
                    if packet_type == "D":
                        # Treat as stdin
                        for event in parser.feed(decode(payload)):
                            self.process_event(event)
                    else:
                        # Process meta information separately
                        self._on_meta(packet_type, payload)
        except _ExitInput:
            pass
        except Exception:
            from traceback import format_exc

            log(format_exc())
        finally:
            input_reader.close()

    def _on_meta(self, packet_type: str, payload: bytes) -> None:
        """Private method to dispatch meta.

        Args:
            packet_type: Packet type (currently always "M")
            payload: Meta payload (JSON encoded as bytes).
        """
        payload_map = json.loads(payload)
        _type = payload_map.get("type", {})
        if isinstance(payload_map, dict):
            self.on_meta(_type, payload_map)

    def on_meta(self, packet_type: str, payload: dict) -> None:
        """Process meta information.

        Args:
            packet_type: The type of the packet.
            payload: meta dict.
        """
        if packet_type == "resize":
            self._size = (payload["width"], payload["height"])
            size = Size(*self._size)
            self._app.post_message(events.Resize(size, size))
        elif packet_type == "focus":
            self._app.post_message(events.AppFocus())
        elif packet_type == "blur":
            self._app.post_message(events.AppBlur())
        elif packet_type == "quit":
            self._app.post_message(messages.ExitApp())
        elif packet_type == "exit":
            raise _ExitInput()
