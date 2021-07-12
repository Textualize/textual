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
        "_no_default_action",
        "_stop_propagation",
    ]

    sender: MessageTarget
    bubble: ClassVar[bool] = False

    def __init__(self, sender: MessageTarget) -> None:
        self.sender = sender
        self.name = camel_to_snake(self.__class__.__name__.replace("Message", ""))
        self.time = monotonic()
        self._no_default_action = False
        self._stop_propagaton = False
        super().__init__()

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield self.sender

    def __init_subclass__(cls, bubble: bool = False) -> None:
        super().__init_subclass__()
        cls.bubble = bubble

    def can_replace(self, message: "Message") -> bool:
        """Check if another message may supersede this one.

        Args:
            message (Message): [description]

        Returns:
            bool: [description]
        """
        return False

    def prevent_default(self, prevent: bool = True) -> None:
        """Suppress the default action.

        Args:
            prevent (bool, optional): True if the default action should be suppressed,
                or False if the default actions should be performed. Defaults to True.
        """
        self._no_default_action = prevent

    def stop_propagation(self, stop: bool = True) -> None:
        self._stop_propagaton = stop
