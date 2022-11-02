from __future__ import annotations

from asyncio import Queue, Task, create_task

from textual._types import EventTarget
from textual.events import InputEvent


class InputQueue:
    def __init__(self, destination: EventTarget):
        self._queue: Queue[InputEvent | None] = Queue()
        self._task: Task | None = None
        self._destination = destination

    async def start(self):
        self._task = create_task(self._process_input())

    async def stop(self):
        await self._queue.put(None)

    async def push(self, event: InputEvent):
        await self._queue.put(event)

    async def _process_input(self) -> None:
        while True:
            input_event = await self._queue.get()
            if input_event is None:
                break
            await self._destination.post_message(input_event)
            await input_event.wait_until_handled()
