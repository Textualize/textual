"""

The Remote driver uses the following packet stricture.

1 byte for packet type. "D" for data, "M" for meta.
4 byte little endian integer for the size of the payload.
Arbitrary payload.


"""

from __future__ import annotations

import asyncio
import json
import os
import selectors
import sys
from codecs import getincrementaldecoder
from functools import partial
from threading import Event, Thread

from .. import events, log
from .._xterm_parser import XTermParser
from ..app import App
from ..driver import Driver
from ..geometry import Size
from ._byte_stream import ByteStream


class WebDriver(Driver):
    """A headless driver that may be run remotely."""

    def __init__(
        self, app: App, *, debug: bool = False, size: tuple[int, int] | None = None
    ):
        super().__init__(app, debug=debug, size=size)
        self.stdout = sys.__stdout__
        self.fileno = sys.__stdout__.fileno()
        self.in_fileno = sys.__stdin__.fileno()
        self._write = partial(os.write, self.fileno)
        self.exit_event = Event()
        self._key_thread: Thread = Thread(target=self.run_input_thread)

    def write(self, data: str) -> None:
        """Write data to the output device.

        Args:
            data: Raw data.
        """

        data_bytes = data.encode("utf-8")
        self._write(b"D%s%s" % (len(data_bytes).to_bytes(4, "big"), data_bytes))

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

        self.write("\x1b[?1049h")  # Alt screen
        self._enable_mouse_support()

        self.write("\x1b[?25l")  # Hide cursor
        self.write("\033[?1003h\n")

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

    def disable_input(self) -> None:
        """Disable further input."""

    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""
        self.exit_event.set()
        self._key_thread.join()

    def run_input_thread(self) -> None:
        """Wait for input and dispatch events."""
        selector = selectors.DefaultSelector()
        fileno = self.in_fileno
        selector.register(fileno, selectors.EVENT_READ)

        def more_data() -> bool:
            """Check if there is more data to parse."""
            for key, events in selector.select(0.01):
                if events:
                    return True
            return False

        parser = XTermParser(more_data, debug=self._debug)
        feed = parser.feed

        utf8_decoder = getincrementaldecoder("utf-8")().decode
        decode = utf8_decoder
        read = os.read
        EVENT_READ = selectors.EVENT_READ

        # The server sends us a stream of bytes, which contains the equivalent of stdin, plus
        # in band data packets.
        byte_stream = ByteStream()
        try:
            while not self.exit_event.is_set():
                selector_events = selector.select(0.1)
                for _selector_key, mask in selector_events:
                    if mask | EVENT_READ:
                        data = read(fileno, 1024)  # raw data

                        for packet_type, payload in byte_stream.feed(data):
                            if packet_type == "D":
                                # Treat as stdin
                                for event in feed(decode(payload)):
                                    self.process_event(event)
                            else:
                                # Process meta information separately
                                self._on_meta(packet_type, payload)
        except Exception as error:
            log(error)
        finally:
            selector.close()

    def _on_meta(self, packet_type: str, payload: bytes) -> None:
        payload_map = json.loads(payload)
        _type = payload_map.get("type")
        if isinstance(payload_map, dict):
            self.on_meta(_type, payload_map)

    def on_meta(self, packet_type: str, payload: dict) -> None:
        if packet_type == "resize":
            self._size = (payload["width"], payload["height"])
            size = Size(*self._size)
            event = events.Resize(size, size)
            asyncio.run_coroutine_threadsafe(
                self._app._post_message(event),
                loop=self._loop,
            )
