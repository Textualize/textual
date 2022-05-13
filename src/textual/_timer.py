from __future__ import annotations

import asyncio
import weakref
from asyncio import (
    CancelledError,
    Event,
    sleep,
    Task,
)
from time import monotonic
from typing import Awaitable, Callable, Union

from rich.repr import Result, rich_repr

from . import events
from ._callback import invoke
from ._types import MessageTarget

TimerCallback = Union[Callable[[], Awaitable[None]], Callable[[], None]]

# /!\ This should only be changed in an "integration tests" context, in which we mock time
_TIMERS_CAN_SKIP: bool = True


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
            sender (MessageTarget): The sender of the event.
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

    def stop_no_wait(self) -> None:
        """Stop the timer."""
        self._task.cancel()

    async def stop(self) -> None:
        """Stop the timer, and block until it exits."""
        self._task.cancel()
        await self._task

    def pause(self) -> None:
        """Pause the timer."""
        self._active.clear()

    def resume(self) -> None:
        """Result a paused timer."""
        self._active.set()

    @staticmethod
    def get_time() -> float:
        """Get the current wall clock time."""
        # N.B. This method will likely be a mocking target in integration tests.
        return monotonic()

    @staticmethod
    async def _sleep(duration: float) -> None:
        # N.B. This method will likely be a mocking target in integration tests.
        await sleep(duration)

    async def _run(self) -> None:
        """Run the timer."""
        count = 0
        _repeat = self._repeat
        _interval = self._interval
        start = self.get_time()
        try:
            while _repeat is None or count <= _repeat:
                next_timer = start + ((count + 1) * _interval)
                if self._skip and _TIMERS_CAN_SKIP and next_timer < self.get_time():
                    count += 1
                    continue
                wait_time = max(0, next_timer - self.get_time())
                if wait_time:
                    await self._sleep(wait_time)
                count += 1
                try:
                    await self._tick(next_timer=next_timer, count=count)
                except EventTargetGone:
                    break
                await self._active.wait()
        except CancelledError:
            pass

    async def _tick(self, *, next_timer: float, count: int) -> None:
        """Triggers the Timer's action: either call its callback, or sends an event to its target"""
        if self._callback is not None:
            await invoke(self._callback)
        else:
            event = events.Timer(
                self.sender,
                timer=self,
                time=next_timer,
                count=count,
                callback=self._callback,
            )

            await self.target.post_priority_message(event)
