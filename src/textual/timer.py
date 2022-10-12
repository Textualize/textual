"""

Timer objects are created by [set_interval][textual.message_pump.MessagePump.set_interval] or
    [set_timer][textual.message_pump.MessagePump.set_timer].

"""

from __future__ import annotations

import asyncio
import weakref
from asyncio import (
    CancelledError,
    Event,
    Task,
)
from typing import Awaitable, Callable, Union

from rich.repr import Result, rich_repr

from . import events
from ._callback import invoke
from ._context import active_app
from . import _clock
from ._types import MessageTarget

TimerCallback = Union[Callable[[], Awaitable[None]], Callable[[], None]]


class EventTargetGone(Exception):
    pass


@rich_repr
class Timer:
    """A class to send timer-based events.

    Args:
        event_target (MessageTarget): The object which will receive the timer events.
        interval (float): The time between timer events.
        sender (MessageTarget): The sender of the event.
        name (str | None, optional): A name to assign the event (for debugging). Defaults to None.
        callback (TimerCallback | None, optional): A optional callback to invoke when the event is handled. Defaults to None.
        repeat (int | None, optional): The number of times to repeat the timer, or None to repeat forever. Defaults to None.
        skip (bool, optional): Enable skipping of scheduled events that couldn't be sent in time. Defaults to True.
        pause (bool, optional): Start the timer paused. Defaults to False.
    """

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
        self._task: Task | None = None
        self._reset: bool = False
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
        self._task = asyncio.create_task(self._run_timer())
        return self._task

    def stop_no_wait(self) -> None:
        """Stop the timer."""
        if self._task is not None:
            self._task.cancel()
            self._task = None

    async def stop(self) -> None:
        """Stop the timer, and block until it exits."""
        if self._task is not None:
            self._active.set()
            self._task.cancel()
            self._task = None

    def pause(self) -> None:
        """Pause the timer.

        A paused timer will not send events until it is resumed.

        """
        self._active.clear()

    def reset(self) -> None:
        """Reset the timer, so it starts from the beginning."""
        self._active.set()
        self._reset = True

    def resume(self) -> None:
        """Resume a paused timer."""
        self._active.set()

    async def _run_timer(self) -> None:
        """Run the timer task."""
        try:
            await self._run()
        except CancelledError:
            pass

    async def _run(self) -> None:
        """Run the timer."""
        count = 0
        _repeat = self._repeat
        _interval = self._interval
        await self._active.wait()
        start = _clock.get_time_no_wait()
        while _repeat is None or count <= _repeat:
            next_timer = start + ((count + 1) * _interval)
            now = await _clock.get_time()
            if self._skip and next_timer < now:
                count += 1
                continue
            now = await _clock.get_time()
            wait_time = max(0, next_timer - now)
            if wait_time:
                await _clock.sleep(wait_time)

            count += 1
            await self._active.wait()
            if self._reset:
                start = _clock.get_time_no_wait()
                count = 0
                self._reset = False
                continue
            try:
                await self._tick(next_timer=next_timer, count=count)
            except EventTargetGone:
                break

    async def _tick(self, *, next_timer: float, count: int) -> None:
        """Triggers the Timer's action: either call its callback, or sends an event to its target"""
        if self._callback is not None:
            try:
                await invoke(self._callback)
            except Exception as error:
                app = active_app.get()
                app._handle_exception(error)
        else:
            event = events.Timer(
                self.sender,
                timer=self,
                time=next_timer,
                count=count,
                callback=self._callback,
            )
            await self.target._post_priority_message(event)
