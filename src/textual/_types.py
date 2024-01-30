from typing import TYPE_CHECKING, Any, Awaitable, Callable, List, Union

from typing_extensions import Protocol

if TYPE_CHECKING:
    from rich.segment import Segment

    from .message import Message


class MessageTarget(Protocol):
    """Protocol that must be followed by objects that can receive messages."""

    async def _post_message(self, message: "Message") -> bool: ...

    def post_message(self, message: "Message") -> bool: ...


class EventTarget(Protocol):
    async def _post_message(self, message: "Message") -> bool: ...

    def post_message(self, message: "Message") -> bool: ...


class UnusedParameter:
    """Helper type for a parameter that isn't specified in a method call."""


SegmentLines = List[List["Segment"]]
CallbackType = Union[Callable[[], Awaitable[None]], Callable[[], None]]
"""Type used for arbitrary callables used in callbacks."""
IgnoreReturnCallbackType = Union[Callable[[], Awaitable[Any]], Callable[[], Any]]
"""A callback which ignores the return type."""
WatchCallbackType = Union[
    Callable[[], Awaitable[None]],
    Callable[[Any], Awaitable[None]],
    Callable[[Any, Any], Awaitable[None]],
    Callable[[], None],
    Callable[[Any], None],
    Callable[[Any, Any], None],
]
"""Type used for callbacks passed to the `watch` method of widgets."""
