from __future__ import annotations

import asyncio
from asyncio import Queue, Task, create_task

from textual._types import EventTarget
from textual.events import Event


class EventQueue:
    def __init__(self, destination: EventTarget):
        self._queue: Queue[Event | None] = Queue()
        self._task: Task | None = None
        self._destination: EventTarget = destination
        self._running: asyncio.Event = asyncio.Event()

    def start(self):
        self._running.set()
        self._task = create_task(self._process_events())

    def pause(self):
        self._running.clear()

    async def shutdown(self):
        await self._queue.put(None)

    async def push(self, event: Event):
        await self._queue.put(event)

    async def _process_events(self) -> None:
        get_event = self._queue.get
        post_message = self._destination.post_message
        wait_until_handled = self._wait_until_handled
        pause = self.pause
        while True:
            event = await get_event()
            if event is None:
                break
            await wait_until_handled()
            await post_message(event)
            pause()

    async def _wait_until_handled(self):
        await self._running.wait()
