import sys
from typing import Awaitable, Callable, Optional, TYPE_CHECKING

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
    async def post_message(
        self,
        message: "Message",
        priority: Optional[int] = None,
    ) -> bool:
        ...


class EventTarget(Protocol):
    async def post_message(
        self,
        message: "Message",
        priority: Optional[int] = None,
    ) -> bool:
        ...


MessageHandler = Callable[["Message"], Awaitable]
