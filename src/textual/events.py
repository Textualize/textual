from __future__ import annotations

from dataclasses import dataclass, field
import re
from enum import auto, Enum
from time import monotonic
from typing import ClassVar, TYPE_CHECKING

from rich.repr import rich_repr, RichReprResult

from .message import Message
from ._types import Callback, MessageTarget
from .keys import Keys


if TYPE_CHECKING:
    from ._timer import Timer as TimerClass
    from ._timer import TimerCallback


class EventType(Enum):
    """Event type enumeration."""

    NONE = auto()
    LOAD = auto()
    STARTUP = auto()
    CREATED = auto()
    IDLE = auto()
    RESIZE = auto()
    MOUNT = auto()
    UNMOUNT = auto()
    SHUTDOWN_REQUEST = auto()
    SHUTDOWN = auto()
    EXIT = auto()
    UPDATED = auto()
    TIMER = auto()
    FOCUS = auto()
    BLUR = auto()
    KEY = auto()
    MOUSE_MOVE = auto()
    MOUSE_DOWN = auto()
    MOUSE_UP = auto()
    MOUSE_SCROLL_DOWN = auto()
    MOUSE_SCROLL_UP = auto()
    CLICK = auto()
    DOUBLE_CLICK = auto()
    ENTER = auto()
    LEAVE = auto()
    UPDATE = auto()
    CUSTOM = 1000


@rich_repr
class Event(Message):
    type: ClassVar[EventType]

    def __rich_repr__(self) -> RichReprResult:
        return
        yield

    def __init_subclass__(
        cls, type: EventType, priority: int = 0, bubble: bool = False
    ) -> None:
        cls.type = type
        super().__init_subclass__(priority=priority, bubble=bubble)

    # def __enter__(self) -> "Event":
    #     return self

    # def __exit__(self, exc_type, exc_value, exc_tb) -> bool | None:
    #     if exc_type is not None:
    #         # Log and suppress exception
    #         return True


class ShutdownRequest(Event, type=EventType.SHUTDOWN_REQUEST):
    pass


class Load(Event, type=EventType.SHUTDOWN_REQUEST):
    pass


class Startup(Event, type=EventType.SHUTDOWN_REQUEST):
    pass


class Created(Event, type=EventType.CREATED):
    pass


class Updated(Event, type=EventType.UPDATED):
    """Indicates the sender was updated and needs a refresh."""


class Idle(Event, type=EventType.IDLE):
    """Sent when there are no more items in the message queue."""


class Resize(Event, type=EventType.RESIZE):
    __slots__ = ["width", "height"]
    width: int
    height: int

    def __init__(self, sender: MessageTarget, width: int, height: int) -> None:
        self.width = width
        self.height = height
        super().__init__(sender)

    def __rich_repr__(self) -> RichReprResult:
        yield self.width
        yield self.height


class Mount(Event, type=EventType.MOUNT):
    pass


class Unmount(Event, type=EventType.UNMOUNT):
    pass


class Shutdown(Event, type=EventType.SHUTDOWN):
    pass


class InputEvent(Event, type=EventType.NONE, bubble=True):
    pass


@rich_repr
class Key(InputEvent, type=EventType.KEY, bubble=True):
    __slots__ = ["key"]

    def __init__(self, sender: MessageTarget, key: Keys | str) -> None:
        super().__init__(sender)
        self.key = key.value if isinstance(key, Keys) else key

    def __rich_repr__(self) -> RichReprResult:
        yield "key", self.key


@rich_repr
class MouseEvent(InputEvent, type=EventType.MOUSE_MOVE):
    __slots__ = ["x", "y", "button"]

    def __init__(
        self,
        sender: MessageTarget,
        x: int,
        y: int,
        button: int,
        shift: bool,
        meta: bool,
        ctrl: bool,
    ) -> None:
        super().__init__(sender)
        self.x = x
        self.y = y
        self.button = button
        self.shift = shift
        self.meta = meta
        self.ctrl = ctrl

    def __rich_repr__(self) -> RichReprResult:
        yield "x", self.x
        yield "y", self.y
        yield "button", self.button, 0
        yield "shift", self.shift, False
        yield "meta", self.meta, False
        yield "ctrl", self.ctrl, False


class MouseMove(MouseEvent, type=EventType.MOUSE_MOVE):
    pass


class MouseDown(MouseEvent, type=EventType.MOUSE_DOWN):
    pass


class MouseUp(MouseEvent, type=EventType.MOUSE_UP):
    pass


class MouseScrollDown(InputEvent, type=EventType.MOUSE_SCROLL_DOWN):
    __slots__ = ["x", "y"]

    def __init__(self, sender: MessageTarget, x: int, y: int) -> None:
        super().__init__(sender)
        self.x = x
        self.y = y


class MouseScrollUp(MouseScrollDown, type=EventType.MOUSE_SCROLL_UP):
    pass


class Click(MouseEvent, type=EventType.CLICK):
    pass


class DoubleClick(MouseEvent, type=EventType.DOUBLE_CLICK):
    pass


@rich_repr
class Timer(Event, type=EventType.TIMER, priority=10):
    __slots__ = ["time", "count", "callback"]

    def __init__(
        self,
        sender: MessageTarget,
        timer: "TimerClass",
        count: int = 0,
        callback: TimerCallback | None = None,
    ) -> None:
        super().__init__(sender)
        self.timer = timer
        self.count = count
        self.callback = callback

    def __rich_repr__(self) -> RichReprResult:
        yield self.timer.name


@rich_repr
class Enter(Event, type=EventType.ENTER):
    __slots__ = ["x", "y"]

    def __init__(self, sender: MessageTarget, x: int, y: int) -> None:
        super().__init__(sender)
        self.x = x
        self.y = y

    def __rich_repr__(self) -> RichReprResult:
        yield "x", self.x
        yield "y", self.y


class Leave(Event, type=EventType.LEAVE):
    pass


class Focus(Event, type=EventType.FOCUS):
    pass


class Blur(Event, type=EventType.BLUR):
    pass


class Update(Event, type=EventType.UPDATE):
    def can_batch(self, event: Message) -> bool:
        return isinstance(event, Update) and event.sender == self.sender
