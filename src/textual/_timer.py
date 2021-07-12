from __future__ import annotations

import weakref
from asyncio import CancelledError, Event, TimeoutError, wait_for
from time import monotonic
from typing import Awaitable, Callable

from rich.repr import RichReprResult, rich_repr

from . import events
from ._types import MessageTarget

TimerCallback = Callable[[], Awaitable[None]]


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
        self._stop_event = Event()
        self._active = Event()
        self._active.set()

    def __rich_repr__(self) -> RichReprResult:
        yield self._interval
        yield "name", self.name
        yield "repeat", self._repeat, None

    @property
    def target(self) -> MessageTarget:
        target = self._target()
        if target is None:
            raise EventTargetGone()
        return target

    def stop(self) -> None:
        self._active.set()
        self._stop_event.set()

    def pause(self) -> None:
        self._active.clear()

    def resume(self) -> None:
        self._active.set()

    async def run(self) -> None:
        count = 0
        _repeat = self._repeat
        _interval = self._interval
        _wait = self._stop_event.wait
        _wait_active = self._active.wait
        start = monotonic()
        try:
            while _repeat is None or count <= _repeat:
                next_timer = start + ((count + 1) * _interval)
                if self._skip and next_timer < monotonic():
                    count += 1
                    continue
                try:
                    if await wait_for(_wait(), max(0, next_timer - monotonic())):
                        break
                except TimeoutError:
                    pass
                event = events.Timer(
                    self.sender, timer=self, count=count, callback=self._callback
                )
                try:
                    await self.target.post_message(event)
                except EventTargetGone:
                    break
                count += 1
                await _wait_active()
        except CancelledError:
            pass
