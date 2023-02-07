from typing import TYPE_CHECKING, Awaitable, Callable, List, Union

from rich.segment import Segment
from typing_extensions import Protocol

if TYPE_CHECKING:
    from .message import Message


class MessageTarget(Protocol):
    async def post_message(self, message: "Message") -> bool:
        ...

    async def _post_priority_message(self, message: "Message") -> bool:
        ...

    def post_message_no_wait(self, message: "Message") -> bool:
        ...


class EventTarget(Protocol):
    async def post_message(self, message: "Message") -> bool:
        ...

    def post_message_no_wait(self, message: "Message") -> bool:
        ...


SegmentLines = List[List["Segment"]]
CallbackType = Union[Callable[[], Awaitable[None]], Callable[[], None]]
