from __future__ import annotations

from asyncio import Event
from time import monotonic
from typing import ClassVar

import rich.repr

from .case import camel_to_snake
from ._types import MessageTarget


@rich.repr.auto
class Message:
    """Base class for a message."""

    __slots__ = [
        "sender",
        "name",
        "time",
        "_forwarded",
        "_no_default_action",
        "_stop_propagation",
        "__done_event",
    ]

    sender: MessageTarget
    bubble: ClassVar[bool] = True
    verbosity: ClassVar[int] = 1

    def __init__(self, sender: MessageTarget) -> None:
        """

        Args:
            sender (MessageTarget): The sender of the message / event.
        """

        self.sender = sender
        self.name = camel_to_snake(self.__class__.__name__.replace("Message", ""))
        self.time = monotonic()
        self._forwarded = False
        self._no_default_action = False
        self._stop_propagation = False
        self.__done_event: Event | None = None
        super().__init__()

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.sender

    def __init_subclass__(cls, bubble: bool = True, verbosity: int = 1) -> None:
        super().__init_subclass__()
        cls.bubble = bubble
        cls.verbosity = verbosity

    @property
    def _done_event(self) -> Event:
        if self.__done_event is None:
            self.__done_event = Event()
        return self.__done_event

    @property
    def is_forwarded(self) -> bool:
        return self._forwarded

    def set_forwarded(self) -> None:
        """Mark this event as being forwarded."""
        self._forwarded = True

    def can_replace(self, message: "Message") -> bool:
        """Check if another message may supersede this one.

        Args:
            message (Message): Another message.

        Returns:
            bool: True if this message may replace the given message
        """
        return False

    def prevent_default(self, prevent: bool = True) -> Message:
        """Suppress the default action.

        Args:
            prevent (bool, optional): True if the default action should be suppressed,
                or False if the default actions should be performed. Defaults to True.
        """
        self._no_default_action = prevent
        return self

    def stop(self, stop: bool = True) -> Message:
        """Stop propagation of the message to parent.

        Args:
            stop (bool, optional): The stop flag. Defaults to True.
        """
        self._stop_propagation = stop
        return self

    async def wait(self) -> None:
        """Wait for the message to be processed."""
        await self._done_event.wait()
