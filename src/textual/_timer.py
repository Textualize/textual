from __future__ import annotations

import asyncio
import weakref
from asyncio import (
    get_event_loop,
    CancelledError,
    Event,
    sleep,
    Task,
)
from functools import partial
from time import monotonic
from typing import Awaitable, Callable, Union

from rich.repr import Result, rich_repr

from . import events
from ._callback import invoke
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
        repeat: int | None = None,
        skip: bool = True,
        pause: bool = False,
    ) -> None:
        """A class to send timer-based events.

        Args:
            event_target (MessageTarget): The object which will receive the timer events.
            interval (float): The time between timer events.
            sender (MessageTarget): The sender of the event.s
            name (str | None, optional): A name to assign the event (for debugging). Defaults to None.
            callback (TimerCallback | None, optional): A optional callback to invoke when the event is handled. Defaults to None.
            repeat (int | None, optional): The number of times to repeat the timer, or None for no repeat. Defaults to None.
            skip (bool, optional): Enable skipping of scheduled events that couldn't be sent in time. Defaults to True.
            pause (bool, optional): Start the timer paused. Defaults to False.
        """
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
        """Start the timer return the task.

        Returns:
            Task: A Task instance for the timer.
        """
        self._task = asyncio.create_task(self._run())
        return self._task

    async def stop(self) -> None:
        """Stop the timer, and block until it exists."""
        self._task.cancel()
        await self._task

    def pause(self) -> None:
        """Pause the timer."""
        self._active.clear()

    def resume(self) -> None:
        """Result a paused timer."""
        self._active.set()

    async def _run(self) -> None:
        """Run the timer."""
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
                    try:
                        await sleep(wait_time)
                    except asyncio.CancelledError:
                        # Likely our program terminating: this is fine, we just have to
                        # shut down out asyncio Task properly:
                        await self.stop()
                event = events.Timer(
                    self.sender,
                    timer=self,
                    time=next_timer,
                    count=count,
                    callback=self._callback,
                )
                count += 1
                try:
                    if self._callback is not None:
                        await invoke(self._callback)
                    else:
                        await self.target.post_priority_message(event)

                except EventTargetGone:
                    break
                await self._active.wait()
        except CancelledError:
            pass
