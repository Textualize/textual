"""

The base class for all messages (including events).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import rich.repr
from typing_extensions import Self

from . import _time
from ._context import active_message_pump
from .case import camel_to_snake

if TYPE_CHECKING:
    from .dom import DOMNode
    from .message_pump import MessagePump


@rich.repr.auto
class Message:
    """Base class for a message."""

    __slots__ = [
        "_sender",
        "time",
        "_forwarded",
        "_no_default_action",
        "_stop_propagation",
        "_prevent",
    ]

    ALLOW_SELECTOR_MATCH: ClassVar[set[str]] = set()
    """Additional attributes that can be used with the [`on` decorator][textual.on].

    These attributes must be widgets.
    """
    bubble: ClassVar[bool] = True  # Message will bubble to parent
    verbose: ClassVar[bool] = False  # Message is verbose
    no_dispatch: ClassVar[bool] = False  # Message may not be handled by client code
    namespace: ClassVar[str] = ""  # Namespace to disambiguate messages
    handler_name: ClassVar[str]
    """Name of the default message handler."""

    def __init__(self) -> None:
        self.__post_init__()

    def __post_init__(self) -> None:
        """Allow dataclasses to initialize the object."""
        self._sender: MessagePump | None = active_message_pump.get(None)
        self.time: float = _time.get_time()
        self._forwarded = False
        self._no_default_action = False
        self._stop_propagation = False
        self._prevent: set[type[Message]] = set()

    def __rich_repr__(self) -> rich.repr.Result:
        yield from ()

    def __init_subclass__(
        cls,
        bubble: bool | None = True,
        verbose: bool = False,
        no_dispatch: bool | None = False,
        namespace: str | None = None,
    ) -> None:
        super().__init_subclass__()
        if bubble is not None:
            cls.bubble = bubble
        cls.verbose = verbose
        if no_dispatch is not None:
            cls.no_dispatch = no_dispatch
        if namespace is not None:
            cls.namespace = namespace
        name = camel_to_snake(cls.__name__)
        cls.handler_name = f"on_{namespace}_{name}" if namespace else f"on_{name}"

    @property
    def control(self) -> DOMNode | None:
        """The widget associated with this message, or None by default."""
        return None

    @property
    def is_forwarded(self) -> bool:
        """Has the message been forwarded?"""
        return self._forwarded

    def _set_forwarded(self) -> None:
        """Mark this event as being forwarded."""
        self._forwarded = True

    def set_sender(self, sender: MessagePump) -> Self:
        """Set the sender of the message.

        Args:
            sender: The sender.

        Note:
            When creating a message the sender is automatically set.
            Normally there will be no need for this method to be called.
            This method will be used when strict control is required over
            the sender of a message.

        Returns:
            Self.
        """
        self._sender = sender
        return self

    def can_replace(self, message: "Message") -> bool:
        """Check if another message may supersede this one.

        Args:
            message: Another message.

        Returns:
            True if this message may replace the given message
        """
        return False

    def prevent_default(self, prevent: bool = True) -> Message:
        """Suppress the default action(s). This will prevent handlers in any base classes
        from being called.

        Args:
            prevent: True if the default action should be suppressed,
                or False if the default actions should be performed.
        """
        self._no_default_action = prevent
        return self

    def stop(self, stop: bool = True) -> Message:
        """Stop propagation of the message to parent.

        Args:
            stop: The stop flag.
        """
        self._stop_propagation = stop
        return self

    def _bubble_to(self, widget: MessagePump) -> None:
        """Bubble to a widget (typically the parent).

        Args:
            widget: Target of bubble.
        """
        widget.post_message(self)
