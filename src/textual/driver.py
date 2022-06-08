from __future__ import annotations

import asyncio
from time import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from . import events
from ._types import MessageTarget

if TYPE_CHECKING:
    from rich.console import Console


class Driver(ABC):
    def __init__(
        self, console: "Console", target: "MessageTarget", debug: bool = False
    ) -> None:
        self.console = console
        self._target = target
        self._debug = debug
        self._loop = asyncio.get_running_loop()
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

    def enable_bracketed_paste(self) -> None:
        """Write the ANSI escape code `ESC[?2004h`, which
        enables bracketed paste mode."""
        self.console.file.write("\x1b[?2004h")
        self.console.file.flush()

    def disable_bracketed_paste(self) -> None:
        """Write the ANSI escape code `ESC[?2004l`, which
        disables bracketed paste mode."""
        self.console.file.write("\x1b[?2004l")
        self.console.file.flush()

    @abstractmethod
    def start_application_mode(self) -> None:
        ...

    @abstractmethod
    def disable_input(self) -> None:
        ...

    @abstractmethod
    def stop_application_mode(self) -> None:
        ...
