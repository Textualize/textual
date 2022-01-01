from __future__ import annotations

import asyncio
from asyncio import CancelledError
from asyncio import Queue, QueueEmpty, Task
from functools import partial
from typing import TYPE_CHECKING, Awaitable, Iterable, Callable
from weakref import WeakSet

from . import events
from . import log
from ._timer import Timer, TimerCallback
from ._callback import invoke
from ._context import active_app
from .message import Message

if TYPE_CHECKING:
    from .app import App


class NoParent(Exception):
    pass


class CallbackError(Exception):
    pass


class MessagePumpClosed(Exception):
    pass


class MessagePump:
    def __init__(self, parent: MessagePump | None = None) -> None:
        self._message_queue: Queue[Message | None] = Queue()
        self._parent = parent
        self._running: bool = False
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

    @property
    def app(self) -> "App":
        """Get the current app."""
        return active_app.get()

    @property
    def is_parent_active(self):
        return self._parent and not self._parent._closed and not self._parent._closing

    @property
    def is_running(self) -> bool:
        return self._running

    def log(self, *args, **kwargs) -> None:
        return self.app.log(*args, **kwargs)

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
        callback: TimerCallback = None,
        *,
        name: str | None = None,
    ) -> Timer:
        timer = Timer(self, delay, self, name=name, callback=callback, repeat=0)
        self._child_tasks.add(timer.start())
        return timer

    def set_interval(
        self,
        interval: float,
        callback: TimerCallback = None,
        *,
        name: str | None = None,
        repeat: int = 0,
    ):
        timer = Timer(
            self, interval, self, name=name, callback=callback, repeat=repeat or None
        )
        self._child_tasks.add(timer.start())
        return timer

    async def call_later(self, callback: Callable, *args, **kwargs) -> None:
        """Run a callback after processing all messages and refreshing the screen.

        Args:
            callback (Callable): A callable.
        """
        await self.post_message(
            events.Callback(self, partial(callback, *args, **kwargs))
        )

    def close_messages_no_wait(self) -> None:
        self._message_queue.put_nowait(None)

    async def close_messages(self) -> None:
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
        self._running = True
        try:
            return await self._process_messages()
        except CancelledError:
            pass
        finally:
            self._running = False

    async def _process_messages(self) -> None:
        """Process messages until the queue is closed."""
        _rich_traceback_guard = True

        while not self._closed:
            try:
                message = await self.get_message()
            except MessagePumpClosed:
                break
            except CancelledError:
                raise
            except Exception as error:
                raise error from None

            # Combine any pending messages that may supersede this one
            while not (self._closed or self._closing):
                pending = self.peek_message()
                if pending is None or not message.can_replace(pending):
                    break
                # self.log(message, "replaced with", pending)
                try:
                    message = await self.get_message()
                except MessagePumpClosed:
                    break

            try:
                await self.dispatch_message(message)
            except CancelledError:
                raise
            except Exception as error:
                self.app.panic()
                break
            finally:
                if isinstance(message, events.Event) and self._message_queue.empty():
                    if not self._closed:
                        event = events.Idle(self)
                        for method in self._get_dispatch_methods("on_idle", event):
                            await method(event)

        log("CLOSED", self)

    async def dispatch_message(self, message: Message) -> bool | None:
        _rich_traceback_guard = True
        try:
            if isinstance(message, events.Event):
                if not isinstance(message, events.Null):
                    await self.on_event(message)
            else:
                return await self.on_message(message)
        finally:
            message._done_event.set()
        return False

    def _get_dispatch_methods(
        self, method_name: str, message: Message
    ) -> Iterable[Callable[[Message], Awaitable]]:
        for cls in self.__class__.__mro__:
            if message._no_default_action:
                break
            method = cls.__dict__.get(method_name, None)
            if method is not None:
                yield method.__get__(self, cls)

    async def on_event(self, event: events.Event) -> None:
        _rich_traceback_guard = True

        for method in self._get_dispatch_methods(f"on_{event.name}", event):
            log(event, ">>>", self, verbosity=event.verbosity)
            await invoke(method, event)

        if event.bubble and self._parent and not event._stop_propagation:
            if event.sender == self._parent:
                # parent is sender, so we stop propagation after parent
                event.stop()
            if self.is_parent_active:
                await self._parent.post_message(event)

    async def on_message(self, message: Message) -> None:
        _rich_traceback_guard = True
        method_name = f"handle_{message.name}"

        method = getattr(self, method_name, None)
        if method is not None:
            log(message, ">>>", self, verbosity=message.verbosity)
            await invoke(method, message)

        if message.bubble and self._parent and not message._stop_propagation:
            if message.sender == self._parent:
                # parent is sender, so we stop propagation after parent
                message.stop()
            if not self._parent._closed and not self._parent._closing:
                await self._parent.post_message(message)

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
            return False

    async def emit(self, message: Message) -> bool:
        if self._parent:
            return await self._parent.post_message_from_child(message)
        else:
            return False

    async def on_timer(self, event: events.Timer) -> None:
        event.prevent_default()
        event.stop()
        if event.callback is not None:
            try:
                await invoke(event.callback)
            except Exception as error:
                raise CallbackError(
                    f"unable to run callback {event.callback!r}; {error}"
                )
