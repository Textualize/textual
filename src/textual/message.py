from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING

import rich.repr

from . import _clock
from .case import camel_to_snake
from ._types import MessageTarget as MessageTarget

if TYPE_CHECKING:
    from .widget import Widget
    from .message_pump import MessagePump


@rich.repr.auto
class Message:
    """Base class for a message.

    Args:
        sender (MessageTarget): The sender of the message / event.

    """

    __slots__ = [
        "sender",
        "name",
        "time",
        "_forwarded",
        "_no_default_action",
        "_stop_propagation",
        "_handler_name",
    ]

    sender: MessageTarget
    bubble: ClassVar[bool] = True  # Message will bubble to parent
    verbose: ClassVar[bool] = False  # Message is verbose
    no_dispatch: ClassVar[bool] = False  # Message may not be handled by client code
    namespace: ClassVar[str] = ""  # Namespace to disambiguate messages

    def __init__(self, sender: MessageTarget) -> None:
        self.sender = sender
        self.name = camel_to_snake(self.__class__.__name__)
        self.time = _clock.get_time_no_wait()
        self._forwarded = False
        self._no_default_action = False
        self._stop_propagation = False
        self._handler_name = (
            f"on_{self.namespace}_{self.name}" if self.namespace else f"on_{self.name}"
        )
        super().__init__()

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.sender

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

    @property
    def is_forwarded(self) -> bool:
        return self._forwarded

    @property
    def handler_name(self) -> str:
        """The name of the handler associated with this message."""
        # Property to make it read only
        return self._handler_name

    def _set_forwarded(self) -> None:
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
        """Suppress the default action(s). This will prevent handlers in any base classes
        from being called.

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

    async def _bubble_to(self, widget: MessagePump) -> None:
        """Bubble to a widget (typically the parent).

        Args:
            widget (Widget): Target of bubble.
        """
        await widget.post_message(self)
