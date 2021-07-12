from __future__ import annotations

import asyncio
import logging
from time import time
import platform
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from . import events
from ._types import MessageTarget

if TYPE_CHECKING:
    from rich.console import Console


log = logging.getLogger("rich")

WINDOWS = platform.system() == "Windows"


class Driver(ABC):
    def __init__(self, console: "Console", target: "MessageTarget") -> None:
        self.console = console
        self._target = target
        self._loop = asyncio.get_event_loop()
        self._mouse_down_time = time()

    def send_event(self, event: events.Event) -> None:
        asyncio.run_coroutine_threadsafe(
            self._target.post_message(event), loop=self._loop
        )

    def process_event(self, event: events.Event) -> None:
        """Performs some additional processing of events."""
        if isinstance(event, events.MouseDown):
            self._mouse_down_time = event.time

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
