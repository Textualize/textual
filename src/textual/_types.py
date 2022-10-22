import sys
from typing import Awaitable, Callable, List, TYPE_CHECKING, Union

from rich.segment import Segment

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
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


Lines = List[List[Segment]]
CallbackType = Union[Callable[[], Awaitable[None]], Callable[[], None]]
