from __future__ import annotations

import asyncio
from asyncio import Queue, Task, create_task

from textual._types import MessageTarget
from textual.events import Event, Key, InputEvent


class EventQueue:
    def __init__(self, destination: MessageTarget):
        self.destination: MessageTarget = destination
        self._queue: Queue[Event | None] = Queue()
        self._task: Task | None = None
        self._accepting_input: asyncio.Event = asyncio.Event()

    def start(self):
        self.enable()
        self._task = create_task(self._process_events())

    def enable(self):
        self._accepting_input.set()

    def disable(self):
        self._accepting_input.clear()

    async def push(self, event: Event):
        await self._queue.put(event)

    async def _process_events(self) -> None:
        get_event = self._queue.get
        post_message = self.destination.post_message
        wait_until_handled = self._wait_until_handled
        disable = self.disable
        while True:
            event = await get_event()
            if event is None:
                self._queue.task_done()
                break

            handle_before_proceeding = isinstance(event, InputEvent)
            if handle_before_proceeding:
                print("disabling input")
                disable()
            await post_message(event)
            if handle_before_proceeding:
                print("enabling input")
                await wait_until_handled()

            self._queue.task_done()

    async def _wait_until_handled(self):
        # TODO: Handle timeouts properly
        try:
            await asyncio.wait_for(self._accepting_input.wait(), timeout=0.5)
        except Exception:
            pass

    async def shutdown(self):
        await self._queue.put(None)
        if self._task:
            await self._task
