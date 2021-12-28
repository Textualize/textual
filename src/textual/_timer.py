from __future__ import annotations

import weakref
from asyncio import (
    get_event_loop,
    CancelledError,
    Event,
    TimeoutError,
    sleep,
    wait,
    wait_for,
    Task,
)
from time import monotonic
from typing import Awaitable, Callable, Union

from rich.repr import Result, rich_repr

from ._profile import timer
from . import log
from . import events
from ._types import MessageTarget

TimerCallback = Union[Callable[[], Awaitable[None]], Callable[[], None]]


class EventTargetGone(Exception):
    pass


@rich_repr
class Timer:
    _timer_count: int = 1

    def __init__(
        self,
        event_target: MessageTarget,
        interval: float,
        sender: MessageTarget,
        *,
        name: str | None = None,
        callback: TimerCallback | None = None,
        repeat: int = None,
        skip: bool = False,
        pause: bool = False,
    ) -> None:
        self._target_repr = repr(event_target)
        self._target = weakref.ref(event_target)
        self._interval = interval
        self.sender = sender
        self.name = f"Timer#{self._timer_count}" if name is None else name
        self._timer_count += 1
        self._callback = callback
        self._repeat = repeat
        self._skip = skip
        self._active = Event()
        if not pause:
            self._active.set()

    def __rich_repr__(self) -> Result:
        yield self._interval
        yield "name", self.name
        yield "repeat", self._repeat, None

    @property
    def target(self) -> MessageTarget:
        target = self._target()
        if target is None:
            raise EventTargetGone()
        return target

    def start(self) -> Task:
        self._task = get_event_loop().create_task(self.run())
        return self._task

    async def stop(self) -> None:
        self._task.cancel()
        await self._task

    async def wait(self) -> None:
        await self._task

    def pause(self) -> None:
        self._active.clear()

    def resume(self) -> None:
        self._active.set()

    async def run(self) -> None:
        count = 0
        _repeat = self._repeat
        _interval = self._interval

        start = monotonic()

        try:
            while _repeat is None or count <= _repeat:
                next_timer = start + ((count + 1) * _interval)
                if self._skip and next_timer < monotonic():
                    count += 1
                    continue
                wait_time = max(0, next_timer - monotonic())
                if wait_time:
                    await sleep(wait_time)

                event = events.Timer(
                    self.sender, timer=self, count=count, callback=self._callback
                )
                count += 1
                try:
                    await self.target.post_message(event)
                except EventTargetGone:
                    break
                await self._active.wait()

        except CancelledError:
            pass
        log(timer_id=id(self))
