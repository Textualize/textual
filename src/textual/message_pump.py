"""

A message pump is a class that processes messages.

It is a base class for the App, Screen, and Widgets.

"""

from __future__ import annotations

import asyncio
import inspect
from asyncio import CancelledError, Queue, QueueEmpty, Task
from functools import partial
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Iterable
from weakref import WeakSet

from . import events, log, messages, Logger
from ._callback import invoke
from ._context import NoActiveAppError, active_app
from .timer import Timer, TimerCallback
from .case import camel_to_snake
from .events import Event
from .message import Message
from .reactive import Reactive

if TYPE_CHECKING:
    from .app import App


class NoParent(Exception):
    pass


class CallbackError(Exception):
    pass


class MessagePumpClosed(Exception):
    pass


class MessagePumpMeta(type):
    """Metaclass for message pump. This exists to populate a Message inner class of a Widget with the
    parent classes' name.

    """

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        class_dict: dict[str, Any],
        **kwargs,
    ):
        namespace = camel_to_snake(name)
        isclass = inspect.isclass
        for value in class_dict.values():
            if isclass(value) and issubclass(value, Message):
                if not value.namespace:
                    value.namespace = namespace
        class_obj = super().__new__(cls, name, bases, class_dict, **kwargs)
        return class_obj


class MessagePump(metaclass=MessagePumpMeta):
    def __init__(self, parent: MessagePump | None = None) -> None:
        self._message_queue: Queue[Message | None] = Queue()
        self._parent = parent
        self._running: bool = False
        self._closing: bool = False
        self._closed: bool = False
        self._disabled_messages: set[type[Message]] = set()
        self._pending_message: Message | None = None
        self._task: Task | None = None
        self._timers: WeakSet[Timer] = WeakSet()

    @property
    def task(self) -> Task:
        assert self._task is not None
        return self._task

    @property
    def has_parent(self) -> bool:
        return self._parent is not None

    @property
    def app(self) -> "App":
        """
        Get the current app.

        Returns:
            App: The current app.

        Raises:
            NoActiveAppError: if no active app could be found for the current asyncio context
        """
        try:
            return active_app.get()
        except LookupError:
            raise NoActiveAppError()

    @property
    def is_parent_active(self) -> bool:
        return bool(
            self._parent and not self._parent._closed and not self._parent._closing
        )

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def log(self) -> Logger:
        """Get a logger for this object.

        Returns:
            Logger: A logger.
        """
        return self.app._logger

    def _attach(self, parent: MessagePump) -> None:
        """Set the parent, and therefore attach this node to the tree.

        Args:
            parent (MessagePump): Parent node.
        """
        self._parent = parent

    def _detach(self) -> None:
        """Set the parent to None to remove the node from the tree."""
        self._parent = None

    def check_message_enabled(self, message: Message) -> bool:
        return type(message) not in self._disabled_messages

    def disable_messages(self, *messages: type[Message]) -> None:
        """Disable message types from being processed."""
        self._disabled_messages.update(messages)

    def enable_messages(self, *messages: type[Message]) -> None:
        """Enable processing of messages types."""
        self._disabled_messages.difference_update(messages)

    async def _get_message(self) -> Message:
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

    def _peek_message(self) -> Message | None:
        """Peek the message at the head of the queue (does not remove it from the queue),
        or return None if the queue is empty.

        Returns:
            Optional[Message]: The message or None.
        """
        if self._pending_message is None:
            try:
                message = self._message_queue.get_nowait()
            except QueueEmpty:
                pass
            else:
                if message is None:
                    self._closed = True
                    raise MessagePumpClosed("The message pump is now closed")
                self._pending_message = message

        if self._pending_message is not None:
            return self._pending_message
        return None

    def set_timer(
        self,
        delay: float,
        callback: TimerCallback | None = None,
        *,
        name: str | None = None,
        pause: bool = False,
    ) -> Timer:
        """Make a function call after a delay.

        Args:
            delay (float): Time to wait before invoking callback.
            callback (TimerCallback | None, optional): Callback to call after time has expired. Defaults to None.
            name (str | None, optional): Name of the timer (for debug). Defaults to None.
            pause (bool, optional): Start timer paused. Defaults to False.

        Returns:
            Timer: A timer object.
        """
        timer = Timer(
            self,
            delay,
            self,
            name=name or f"set_timer#{Timer._timer_count}",
            callback=callback,
            repeat=0,
            pause=pause,
        )
        timer.start()
        self._timers.add(timer)
        return timer

    def set_interval(
        self,
        interval: float,
        callback: TimerCallback | None = None,
        *,
        name: str | None = None,
        repeat: int = 0,
        pause: bool = False,
    ) -> Timer:
        """Call a function at periodic intervals.

        Args:
            interval (float): Time between calls.
            callback (TimerCallback | None, optional): Function to call. Defaults to None.
            name (str | None, optional): Name of the timer object. Defaults to None.
            repeat (int, optional): Number of times to repeat the call or 0 for continuous. Defaults to 0.
            pause (bool, optional): Start the timer paused. Defaults to False.

        Returns:
            Timer: A timer object.
        """
        timer = Timer(
            self,
            interval,
            self,
            name=name or f"set_interval#{Timer._timer_count}",
            callback=callback,
            repeat=repeat or None,
            pause=pause,
        )
        timer.start()
        self._timers.add(timer)
        return timer

    def call_later(self, callback: Callable, *args, **kwargs) -> None:
        """Schedule a callback to run after all messages are processed and the screen
        has been refreshed. Positional and keyword arguments are passed to the callable.

        Args:
            callback (Callable): A callable.
        """
        # We send the InvokeLater message to ourselves first, to ensure we've cleared
        # out anything already pending in our own queue.
        message = messages.InvokeLater(self, partial(callback, *args, **kwargs))
        self.post_message_no_wait(message)

    def _on_invoke_later(self, message: messages.InvokeLater) -> None:
        # Forward InvokeLater message to the Screen
        self.app.screen._invoke_later(message.callback)

    def _close_messages_no_wait(self) -> None:
        """Request the message queue to exit."""
        self._message_queue.put_nowait(None)

    async def _close_messages(self) -> None:
        """Close message queue, and optionally wait for queue to finish processing."""
        if self._closed or self._closing:
            return
        self._closing = True
        stop_timers = list(self._timers)
        for timer in stop_timers:
            await timer.stop()
        self._timers.clear()
        await self._message_queue.put(None)

        if self._task is not None and asyncio.current_task() != self._task:
            # Ensure everything is closed before returning
            await self._task

    def _start_messages(self) -> None:
        """Start messages task."""
        self._task = asyncio.create_task(self._process_messages())

    async def _process_messages(self) -> None:
        self._running = True
        try:
            await self._process_messages_loop()
        except CancelledError:
            pass
        finally:
            self._running = False
            for timer in list(self._timers):
                await timer.stop()

    async def _process_messages_loop(self) -> None:
        """Process messages until the queue is closed."""
        _rich_traceback_guard = True

        await Reactive.initialize_object(self)
        while not self._closed:
            try:
                message = await self._get_message()
            except MessagePumpClosed:
                break
            except CancelledError:
                raise
            except Exception as error:
                raise error from None

            # Combine any pending messages that may supersede this one
            while not (self._closed or self._closing):
                try:
                    pending = self._peek_message()
                except MessagePumpClosed:
                    break
                if pending is None or not message.can_replace(pending):
                    break
                try:
                    message = await self._get_message()
                except MessagePumpClosed:
                    break

            try:
                await self._dispatch_message(message)
            except CancelledError:
                raise
            except Exception as error:
                self.app._handle_exception(error)
                break
            finally:
                self._message_queue.task_done()
                if self._message_queue.empty():
                    if not self._closed:
                        event = events.Idle(self)
                        for _cls, method in self._get_dispatch_methods(
                            "on_idle", event
                        ):
                            try:
                                await invoke(method, event)
                            except Exception as error:
                                self.app._handle_exception(error)
                                break

        log("CLOSED", self)

    async def _dispatch_message(self, message: Message) -> None:
        """Dispatch a message received from the message queue.

        Args:
            message (Message): A message object
        """
        _rich_traceback_guard = True
        if message.no_dispatch:
            return

        # Allow apps to treat events and messages separately
        if isinstance(message, Event):
            await self.on_event(message)
        else:
            await self._on_message(message)

    def _get_dispatch_methods(
        self, method_name: str, message: Message
    ) -> Iterable[tuple[type, Callable[[Message], Awaitable]]]:
        """Gets handlers from the MRO

        Args:
            method_name (str): Handler method name.
            message (Message): Message object.

        """
        private_method = f"_{method_name}"
        for cls in self.__class__.__mro__:
            if message._no_default_action:
                break
            method = cls.__dict__.get(private_method) or cls.__dict__.get(method_name)
            if method is not None:
                yield cls, method.__get__(self, cls)

    async def on_event(self, event: events.Event) -> None:
        """Called to process an event.

        Args:
            event (events.Event): An Event object.
        """
        await self._on_message(event)

    async def _on_message(self, message: Message) -> None:
        """Called to process a message.

        Args:
            message (Message): A Message object.
        """
        _rich_traceback_guard = True
        handler_name = message._handler_name

        # Look through the MRO to find a handler
        for cls, method in self._get_dispatch_methods(handler_name, message):
            log.event.verbosity(message.verbose)(
                message,
                ">>>",
                self,
                f"method=<{cls.__name__}.{handler_name}>",
            )
            await invoke(method, message)

        # Bubble messages up the DOM (if enabled on the message)
        if message.bubble and self._parent and not message._stop_propagation:
            if message.sender == self._parent:
                # parent is sender, so we stop propagation after parent
                message.stop()
            if self.is_parent_active and not self._parent._closing:
                await message._bubble_to(self._parent)

    def check_idle(self) -> None:
        """Prompt the message pump to call idle if the queue is empty."""
        if self._message_queue.empty():
            self.post_message_no_wait(messages.Prompt(sender=self))

    async def post_message(self, message: Message) -> bool:
        """Post a message or an event to this message pump.

        Args:
            message (Message): A message object.

        Returns:
            bool: True if the messages was posted successfully, False if the message was not posted
                (because the message pump was in the process of closing).
        """

        if self._closing or self._closed:
            return False
        if not self.check_message_enabled(message):
            return True
        await self._message_queue.put(message)
        return True

    # TODO: This may not be needed, or may only be needed by the timer
    # Consider removing or making private
    async def _post_priority_message(self, message: Message) -> bool:
        """Post a "priority" messages which will be processes prior to regular messages.

        Note that you should rarely need this in a regular app. It exists primarily to allow
        timer messages to skip the queue, so that they can be more regular.

        Args:
            message (Message): A message.

        Returns:
            bool: True if the messages was processed, False if it wasn't.
        """
        # TODO: Allow priority messages to jump the queue
        if self._closing or self._closed:
            return False
        if not self.check_message_enabled(message):
            return False
        await self._message_queue.put(message)
        return True

    def post_message_no_wait(self, message: Message) -> bool:
        """Posts a message on the queue.

        Args:
            message (Message): A message (or Event).

        Returns:
            bool: True if the messages was processed, False if it wasn't.
        """
        if self._closing or self._closed:
            return False
        if not self.check_message_enabled(message):
            return False
        self._message_queue.put_nowait(message)
        return True

    async def _post_message_from_child(self, message: Message) -> bool:
        if self._closing or self._closed:
            return False
        return await self.post_message(message)

    def _post_message_from_child_no_wait(self, message: Message) -> bool:
        if self._closing or self._closed:
            return False
        return self.post_message_no_wait(message)

    async def on_callback(self, event: events.Callback) -> None:
        await invoke(event.callback)

    def emit_no_wait(self, message: Message) -> bool:
        """Send a message to the _parent_, non async version.

        Args:
            message (Message): A message object.

        Returns:
            bool: True if the message was posted successfully.
        """
        if self._parent:
            return self._parent._post_message_from_child_no_wait(message)
        else:
            return False

    async def emit(self, message: Message) -> bool:
        """Send a message to the _parent_.

        Args:
            message (Message): A message object.

        Returns:
            bool: True if the message was posted successfully.
        """
        if self._parent:
            return await self._parent._post_message_from_child(message)
        else:
            return False

    # TODO: Does dispatch_key belong on message pump?
    async def dispatch_key(self, event: events.Key) -> bool:
        """Dispatch a key event to method.

        This method will call the method named 'key_<event.key>' if it exists.

        Args:
            event (events.Key): A key event.

        Returns:
            bool: True if key was handled, otherwise False.
        """
        key_method = getattr(self, f"key_{event.key_name}", None) or getattr(
            self, f"_key_{event.key_name}", None
        )
        if key_method is not None:
            await invoke(key_method, event)
            return True
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
