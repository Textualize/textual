from __future__ import annotations

import asyncio
from asyncio import Event
from collections import deque
from typing import Generic, TypeVar

QueueType = TypeVar("QueueType")


class Queue(Generic[QueueType]):
    """A cut-down version of asyncio.Queue

    This has just enough functionality to run the message pumps.

    """

    def __init__(self) -> None:
        self.values: deque[QueueType] = deque()
        self.ready_event = Event()

    def put_nowait(self, value: QueueType) -> None:
        self.values.append(value)
        self.ready_event.set()

    def qsize(self) -> int:
        return len(self.values)

    def empty(self) -> bool:
        return not self.values

    def task_done(self) -> None:
        pass

    async def get(self) -> QueueType:
        if not self.ready_event.is_set():
            await self.ready_event.wait()
        value = self.values.popleft()
        if not self.values:
            self.ready_event.clear()
        return value

    def get_nowait(self) -> QueueType:
        if not self.values:
            raise asyncio.QueueEmpty()
        value = self.values.popleft()
        if not self.values:
            self.ready_event.clear()
        return value
