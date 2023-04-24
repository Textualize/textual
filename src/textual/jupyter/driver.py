from __future__ import annotations

import asyncio
import queue
from threading import Event, Thread

from aiohttp import web

from .. import events, log
from .._xterm_parser import XTermParser
from ..app import App
from ..driver import Driver
from ..geometry import Size


class JupyterDriver(Driver):
    """A headless driver that may be run remotely."""

    def __init__(
        self,
        websocket: web.WebSocketResponse,
        app: App,
        *,
        debug: bool = False,
        size: tuple[int, int] | None = None,
    ) -> None:
        super().__init__(app, debug=debug, size=size)
        self.websocket = websocket

        self.exit_event = Event()
        self._key_thread: Thread = Thread(target=self.run_input_thread)
        self.stdin_queue: queue.Queue[str | None] = queue.Queue()

    def write(self, data: str) -> None:
        """Write data to the output device.

        Args:
            data: Raw data.
        """

        asyncio.run_coroutine_threadsafe(
            self.websocket.send_bytes(data.encode("utf-8")),
            loop=self._loop,
        )

        # loop.call_soon_threadsafe(self.websocket.send_bytes, data.encode("utf-8"))

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

        self.write("HELLO")

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
        self.stdin_queue.put(None)
        self._key_thread.join()

    def feed_stdin(self, data: str | None) -> None:
        self.stdin_queue.put(data)

    def run_input_thread(self) -> None:
        """Wait for input and dispatch events."""

        def more_data() -> bool:
            """Check if there is more data to parse."""
            return False

        parser = XTermParser(more_data, debug=self._debug)
        feed = parser.feed

        # The server sends us a stream of bytes, which contains the equivalent of stdin, plus
        # in band data packets.

        try:
            while not self.exit_event.is_set():
                try:
                    data = self.stdin_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                if data is None:
                    break

                log("READ DATA", repr(data))

                for event in feed(data):
                    self.process_event(event)

        except Exception as error:
            log(error)

    def on_meta(self, packet_type: str, payload: dict) -> None:
        if packet_type == "resize":
            self._size = (payload["width"], payload["height"])
            size = Size(*self._size)
            event = events.Resize(size, size)
            asyncio.run_coroutine_threadsafe(
                self._app._post_message(event),
                loop=self._loop,
            )
