from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import IO

from . import _time, events
from ._types import MessageTarget
from .events import MouseUp


class Driver(ABC):
    """A base class for drivers."""

    def __init__(
        self,
        file: IO[str],
        target: "MessageTarget",
        *,
        debug: bool = False,
        size: tuple[int, int] | None = None,
    ) -> None:
        """Initialize a driver.

        Args:
            file: A file-like object open for writing unicode.
            target: The message target (expected to be the app).
            debug: Enabled debug mode.
            size: Initial size of the terminal or `None` to detect.
        """
        self._file = file
        self._target = target
        self._debug = debug
        self._size = size
        self._loop = asyncio.get_running_loop()
        self._mouse_down_time = _time.get_time()
        self._down_buttons: list[int] = []
        self._last_move_event: events.MouseMove | None = None

    @property
    def is_headless(self) -> bool:
        """Is the driver 'headless' (no output)?"""
        return False

    def send_event(self, event: events.Event) -> None:
        """Send an event to the target app.

        Args:
            event: An event.
        """
        asyncio.run_coroutine_threadsafe(
            self._target._post_message(event), loop=self._loop
        )

    def process_event(self, event: events.Event) -> None:
        """Perform additional processing on an event, prior to sending.

        Args:
            event: An event to send.
        """
        event._set_sender(self._target)
        if isinstance(event, events.MouseDown):
            self._mouse_down_time = event.time
            if event.button:
                self._down_buttons.append(event.button)
        elif isinstance(event, events.MouseUp):
            if event.button:
                self._down_buttons.remove(event.button)
        elif isinstance(event, events.MouseMove):
            if (
                self._down_buttons
                and not event.button
                and self._last_move_event is not None
            ):
                # Deduplicate self._down_buttons while preserving order.
                buttons = list(dict.fromkeys(self._down_buttons).keys())
                self._down_buttons.clear()
                move_event = self._last_move_event
                for button in buttons:
                    self.send_event(
                        MouseUp(
                            x=move_event.x,
                            y=move_event.y,
                            delta_x=0,
                            delta_y=0,
                            button=button,
                            shift=event.shift,
                            meta=event.meta,
                            ctrl=event.ctrl,
                            screen_x=move_event.screen_x,
                            screen_y=move_event.screen_y,
                            style=event.style,
                        )
                    )
            self._last_move_event = event

        self.send_event(event)

        if (
            isinstance(event, events.MouseUp)
            and event.time - self._mouse_down_time <= 0.5
        ):
            click_event = events.Click.from_event(event)
            self.send_event(click_event)

    def flush(self) -> None:
        """Flush any buffered data."""

    @abstractmethod
    def write(self, data: str) -> None:
        """Write data to the output device.

        Args:
            data: Raw data.
        """

    @abstractmethod
    def start_application_mode(self) -> None:
        """Start application mode."""

    @abstractmethod
    def disable_input(self) -> None:
        """Disable further input."""

    @abstractmethod
    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""
