from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from . import _clock, events
from ._types import MessageTarget
from .events import MouseUp

if TYPE_CHECKING:
    from rich.console import Console


class Driver(ABC):
    def __init__(
        self,
        console: "Console",
        target: "MessageTarget",
        *,
        debug: bool = False,
        size: tuple[int, int] | None = None,
    ) -> None:
        self.console = console
        self._target = target
        self._debug = debug
        self._size = size
        self._loop = asyncio.get_running_loop()
        self._mouse_down_time = _clock.get_time_no_wait()
        self._dragging = False

    @property
    def is_headless(self) -> bool:
        """Check if the driver is 'headless'"""
        return False

    def send_event(self, event: events.Event) -> None:
        asyncio.run_coroutine_threadsafe(
            self._target._post_message(event), loop=self._loop
        )

    def process_event(self, event: events.Event) -> None:
        """Performs some additional processing of events."""
        if isinstance(event, events.MouseDown):
            self._mouse_down_time = event.time
        elif isinstance(event, events.MouseMove):
            if event.button and not self._dragging:
                self._dragging = True
            elif self._dragging and not event.button:
                # Artificially generate a MouseUp event when we stop "dragging"
                self.send_event(
                    MouseUp(
                        x=event.x,
                        y=event.y,
                        delta_x=event.delta_x,
                        delta_y=event.delta_y,
                        button=0,
                        shift=event.shift,
                        meta=event.meta,
                        ctrl=event.ctrl,
                        screen_x=event.screen_x,
                        screen_y=event.screen_y,
                        style=event.style,
                    )
                )
                self._dragging = False

        self.send_event(event)

        if (
            isinstance(event, events.MouseUp)
            and event.time - self._mouse_down_time <= 0.5
        ):
            click_event = events.Click.from_event(event)
            self.send_event(click_event)

    @abstractmethod
    def start_application_mode(self) -> None:
        ...

    @abstractmethod
    def disable_input(self) -> None:
        ...

    @abstractmethod
    def stop_application_mode(self) -> None:
        ...
