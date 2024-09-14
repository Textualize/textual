from typing import TYPE_CHECKING, Any, Awaitable, Callable, List, Literal, Union

from typing_extensions import Protocol

if TYPE_CHECKING:
    from rich.segment import Segment

    from textual.message import Message


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
WatchCallbackBothValuesType = Union[
    Callable[[Any, Any], Awaitable[None]],
    Callable[[Any, Any], None],
]
"""Type for watch methods that accept the old and new values of reactive objects."""
WatchCallbackNewValueType = Union[
    Callable[[Any], Awaitable[None]],
    Callable[[Any], None],
]
"""Type for watch methods that accept only the new value of reactive objects."""
WatchCallbackNoArgsType = Union[
    Callable[[], Awaitable[None]],
    Callable[[], None],
]
"""Type for watch methods that do not require the explicit value of the reactive."""
WatchCallbackType = Union[
    WatchCallbackBothValuesType,
    WatchCallbackNewValueType,
    WatchCallbackNoArgsType,
]
"""Type used for callbacks passed to the `watch` method of widgets."""

AnimationLevel = Literal["none", "basic", "full"]
"""The levels that the [`TEXTUAL_ANIMATIONS`][textual.constants.TEXTUAL_ANIMATIONS] env var can be set to."""
