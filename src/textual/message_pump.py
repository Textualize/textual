from __future__ import annotations

from typing import Any, Coroutine, Awaitable, NamedTuple
import asyncio
from asyncio import Event, Queue, Task, QueueEmpty

import logging

from . import events
from .message import Message
from ._timer import Timer, TimerCallback
from ._types import MessageHandler

log = logging.getLogger("rich")


class MessagePumpClosed(Exception):
    pass


class MessagePump:
    def __init__(self, queue_size: int = 10, parent: MessagePump | None = None) -> None:
        self._message_queue: Queue[Message | None] = Queue()
        self._parent = parent
        self._closing: bool = False
        self._closed: bool = False
        self._disabled_messages: set[type[Message]] = set()
        self._pending_message: Message | None = None
        self._task: Task | None = None
        self._child_tasks: set[Task] = set()
        self._queue_empty_event = Event()

    @property
    def task(self) -> Task:
        assert self._task is not None
        return self._task

    def set_parent(self, parent: MessagePump) -> None:
        self._parent = parent

    def check_message_enabled(self, message: Message) -> bool:
        return type(message) not in self._disabled_messages

    def disable_messages(self, *messages: type[Message]) -> None:
        """Disable message types from being processed."""
        self._disabled_messages.update(messages)

    def enable_messages(self, *messages: type[Message]) -> None:
        """Enable processing of messages types."""
        self._disabled_messages.difference_update(messages)

    async def get_message(self) -> Message:
        """Get the next event on the queue, or None if queue is closed.

        Returns:
            Optional[Event]: Event object or None.
        """
        if self._closed:
            raise MessagePumpClosed("The message pump is closed")
        if self._pending_message is not None:
            try:
                return self._pending_message
            finally:
                self._pending_message = None
        message = await self._message_queue.get()
        if message is None:
            self._closed = True
            raise MessagePumpClosed("The message pump is now closed")
        return message

    def peek_message(self) -> Message | None:
        """Peek the message at the head of the queue (does not remove it from the queue),
        or return None if the queue is empty.

        Returns:
            Optional[Message]: The message or None.
        """
        if self._pending_message is None:
            try:
                self._pending_message = self._message_queue.get_nowait()
            except QueueEmpty:
                pass

        if self._pending_message is not None:
            return self._pending_message
        return None

    def set_timer(
        self,
        delay: float,
        *,
        name: str | None = None,
        callback: TimerCallback = None,
    ) -> Timer:
        timer = Timer(self, delay, self, name=name, callback=callback, repeat=0)
        timer_task = asyncio.get_event_loop().create_task(timer.run())
        self._child_tasks.add(timer_task)
        return timer

    def set_interval(
        self,
        interval: float,
        *,
        name: str | None = None,
        callback: TimerCallback = None,
        repeat: int = 0,
    ):
        timer = Timer(
            self, interval, self, name=name, callback=callback, repeat=repeat or None
        )
        asyncio.get_event_loop().create_task(timer.run())
        return timer

    async def stop_messages(self) -> None:
        if not self._closing:
            await self.post_message(events.NoneEvent(self))
            self._closing = True
        return
        if not (self._closing or self._closed):
            self._queue_empty_event.clear()
            await self.post_message(events.NoneEvent(self))
            self._closing = True
            await self._queue_empty_event.wait()
            self._queue_empty_event.clear()

    async def close_messages(self, wait: bool = True) -> None:
        """Close message queue, and optionally wait for queue to finish processing."""
        if self._closed:
            return
        log.debug("close_messages %r wait=%r", self, wait)
        self._closing = True
        log.debug("close 1 %r", self)
        for task in self._child_tasks:
            task.cancel()
        log.debug("close 2 %r", self)
        await self._message_queue.put(None)
        log.debug("close 3 %r", self)
        if wait and self._task is not None:
            await self._task
            self._task = None
        log.debug("close 4 %r", self)

    def start_messages(self) -> None:
        self._task = asyncio.create_task(self.process_messages())

    async def process_messages(self) -> None:
        """Process messages until the queue is closed."""
        while not self._closed:
            try:
                message = await self.get_message()
            except MessagePumpClosed:
                log.debug("CLOSED %r", self)
                break
            except Exception as error:
                log.exception("error in get_message()")
                raise error from None

            log.debug("%r -> %r", message, self)
            # Combine any pending messages that may supersede this one
            while True:
                pending = self.peek_message()
                if pending is None or not message.can_batch(pending):
                    break
                try:
                    message = await self.get_message()
                except MessagePumpClosed:
                    break

            try:
                await self.dispatch_message(message)
            except Exception as error:
                log.exception("error in dispatch_message")
                raise
            finally:
                log.debug("a")
                if self._message_queue.empty():
                    log.debug("b")
                    self._queue_empty_event.set()
                    if not self._closed:
                        idle_handler = getattr(self, "on_idle", None)
                        log.debug("c %r", idle_handler)
                        if idle_handler is not None and not self._closed:
                            log.debug("d")
                            await idle_handler(events.Idle(self))
                            log.debug("e")
        self._queue_empty_event.set()

    async def dispatch_message(self, message: Message) -> bool | None:
        log.debug("dispatch_message %r", message)
        if isinstance(message, events.Event):
            await self.on_event(message)
        else:
            return await self.on_message(message)
        return False

    async def on_event(self, event: events.Event) -> None:
        method_name = f"on_{event.name}"
        dispatch_function: MessageHandler = getattr(self, method_name, None)
        log.debug("dispatching to %r", dispatch_function)
        if dispatch_function is not None:
            await dispatch_function(event)
        if event.bubble and self._parent and not event._stop_propagaton:
            if event.sender == self._parent:
                log.debug("bubbled event abandoned; %r", event)
            elif not self._parent._closed and not self._parent._closing:
                await self._parent.post_message(event)

    async def on_message(self, message: Message) -> None:
        pass

    def post_message_no_wait(self, message: Message) -> bool:
        if self._closing or self._closed:
            return False
        if not self.check_message_enabled(message):
            return True
        self._message_queue.put_nowait(message)
        return True

    async def post_message(self, message: Message) -> bool:
        log.debug("%r post_message 1", self)
        if self._closing or self._closed:
            return False
        log.debug("%r post_message 2", self)
        if not self.check_message_enabled(message):
            return True
        log.debug("%r post_message 3", self)
        await self._message_queue.put(message)
        log.debug("%r post_message 4", self)
        return True

    async def post_message_from_child(self, message: Message) -> bool:
        if self._closing or self._closed:
            return False
        return await self.post_message(message)

    async def emit(self, message: Message) -> bool:
        if self._parent:
            await self._parent.post_message_from_child(message)
            return True
        else:
            return False

    async def on_timer(self, event: events.Timer) -> None:
        if event.callback is not None:
            await event.callback()
