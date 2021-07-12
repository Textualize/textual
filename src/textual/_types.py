import sys
from typing import Awaitable, Callable, List, Optional, TYPE_CHECKING
from rich.segment import Segment

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


if TYPE_CHECKING:
    from .events import Event
    from .message import Message

Callback = Callable[[], None]
# IntervalID = int


class MessageTarget(Protocol):
    async def post_message(self, message: "Message") -> bool:
        ...

    def post_message_no_wait(self, message: "Message") -> bool:
        ...


class EventTarget(Protocol):
    async def post_message(self, message: "Message") -> bool:
        ...

    def post_message_no_wait(self, message: "Message") -> bool:
        ...


MessageHandler = Callable[["Message"], Awaitable]

Lines = List[List[Segment]]
