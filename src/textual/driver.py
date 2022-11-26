from __future__ import annotations
import threading

import anyio.abc
import anyio.from_thread
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from . import _clock, events
from ._types import MessageTarget

if TYPE_CHECKING:
    from rich.console import Console


class Driver(ABC):
    def __init__(
        self,
        console: "Console",
        target: "MessageTarget",
        task_group: anyio.abc.TaskGroup,
        *,
        debug: bool = False,
        size: tuple[int, int] | None = None,
    ) -> None:
        self.console = console
        self._target = target
        self._task_group = task_group
        self._debug = debug
        self._size = size
        self._mouse_down_time = _clock.get_time_no_wait()

    @property
    def is_headless(self) -> bool:
        """Check if the driver is 'headless'"""
        return False

    def send_event(self, event: events.Event) -> None:
        self._task_group.start_soon(self._target.post_message, event)

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

    async def _start_thread_portal(self) -> anyio.from_thread.BlockingPortal:
        """
        Starts a blocking portal, which can be used to call back into the event
        loop from a thread.
        """

        async def portal_task(*, task_status=anyio.TASK_STATUS_IGNORED):
            async with anyio.from_thread.BlockingPortal() as portal:
                task_status.started(portal)
                await portal.sleep_until_stopped()

        return await self._task_group.start(portal_task)

    @abstractmethod
    async def start_application_mode(self) -> None:
        ...

    @abstractmethod
    async def disable_input(self) -> None:
        ...

    @abstractmethod
    def stop_application_mode(self) -> None:
        ...
