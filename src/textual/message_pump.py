from __future__ import annotations

import asyncio
import logging
from asyncio import Event, Queue, QueueEmpty, Task
from typing import Any, Awaitable, Coroutine, NamedTuple
from weakref import WeakSet

from . import events
from ._timer import Timer, TimerCallback
from ._types import MessageHandler
from .message import Message

log = logging.getLogger("rich")


class NoParent(Exception):
    pass


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
        self._child_tasks: WeakSet[Task] = WeakSet()

    @property
    def task(self) -> Task:
        assert self._task is not None
        return self._task

    @property
    def parent(self) -> MessagePump:
        if self._parent is None:
            raise NoParent(f"{self._parent} has no parent")
        return self._parent

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
        self._child_tasks.add(asyncio.get_event_loop().create_task(timer.run()))
        return timer

    async def close_messages(self, wait: bool = True) -> None:
        """Close message queue, and optionally wait for queue to finish processing."""
        if self._closed:
            return

        self._closing = True

        await self._message_queue.put(None)

        for task in self._child_tasks:
            task.cancel()
            await task
        self._child_tasks.clear()

    def start_messages(self) -> None:
        self._task = asyncio.create_task(self.process_messages())

    async def process_messages(self) -> None:
        """Process messages until the queue is closed."""
        while not self._closed:
            try:
                message = await self.get_message()
            except MessagePumpClosed:
                break
            except Exception as error:
                log.exception("error in get_message()")
                raise error from None

            log.debug("%r -> %r", message, self)
            # Combine any pending messages that may supersede this one
            while not (self._closed or self._closing):
                pending = self.peek_message()
                if pending is None or not message.can_replace(pending):
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
                if isinstance(message, events.Event) and self._message_queue.empty():
                    if not self._closed:
                        idle_handler = getattr(self, "on_idle", None)
                        if idle_handler is not None and not self._closed:
                            await idle_handler(events.Idle(self))

        log.debug("CLOSED %r", self)

    async def dispatch_message(self, message: Message) -> bool | None:
        _rich_traceback_guard = True
        if isinstance(message, events.Event):
            if not isinstance(message, events.Null):
                await self.on_event(message)
        else:
            return await self.on_message(message)
        return False

    async def on_event(self, event: events.Event) -> None:
        method_name = f"on_{event.name}"

        dispatch_function: MessageHandler = getattr(self, method_name, None)
        if dispatch_function is not None:
            await dispatch_function(event)
        if event.bubble and self._parent and not event._stop_propagaton:
            if event.sender == self._parent:
                pass
                # log.debug("bubbled event abandoned; %r", event)
            elif not self._parent._closed and not self._parent._closing:
                await self._parent.post_message(event)

    async def on_message(self, message: Message) -> None:
        method_name = f"message_{message.name}"
        method = getattr(self, method_name, None)
        if method is not None:
            await method(message)

    def post_message_no_wait(self, message: Message) -> bool:
        if self._closing or self._closed:
            return False
        if not self.check_message_enabled(message):
            return True
        self._message_queue.put_nowait(message)
        return True

    async def post_message(self, message: Message) -> bool:
        if self._closing or self._closed:
            return False
        if not self.check_message_enabled(message):
            return True
        await self._message_queue.put(message)
        return True

    def post_message_from_child_no_wait(self, message: Message) -> bool:
        if self._closing or self._closed:
            return False
        return self.post_message_no_wait(message)

    async def post_message_from_child(self, message: Message) -> bool:
        if self._closing or self._closed:
            return False
        return await self.post_message(message)

    async def on_callback(self, event: events.Callback) -> None:
        await event.callback()

    def emit_no_wait(self, message: Message) -> bool:
        if self._parent:
            return self._parent.post_message_from_child_no_wait(message)
        else:
            log.warning("NO PARENT %r %r", self, message)
            return False

    async def emit(self, message: Message) -> bool:
        if self._parent:
            return await self._parent.post_message_from_child(message)
        else:
            log.warning("NO PARENT %r %r", self, message)
            return False

    async def on_timer(self, event: events.Timer) -> None:
        if event.callback is not None:
            await event.callback()
