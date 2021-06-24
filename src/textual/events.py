from __future__ import annotations

from typing import TYPE_CHECKING

from rich.repr import rich_repr, RichReprResult

from .message import Message
from ._types import MessageTarget
from .keys import Keys


if TYPE_CHECKING:
    from ._timer import Timer as TimerClass
    from ._timer import TimerCallback


@rich_repr
class Event(Message):
    def __rich_repr__(self) -> RichReprResult:
        return
        yield

    def __init_subclass__(cls, bubble: bool = False) -> None:
        super().__init_subclass__(bubble=bubble)


class Null(Event):
    def can_batch(self, event: Event) -> bool:
        return isinstance(event, Null)


class Repaint(Event):
    def can_batch(self, event: Event) -> bool:
        return isinstance(event, Repaint)


class ShutdownRequest(Event):
    pass


class Shutdown(Event):
    pass


class Load(Event):
    pass


class Startup(Event):
    pass


class Created(Event):
    pass


class Updated(Event):
    """Indicates the sender was updated and needs a refresh."""


class Idle(Event):
    """Sent when there are no more items in the message queue."""


class Action(Event):
    __slots__ = ["action"]

    def __init__(self, sender: MessageTarget, action: str) -> None:
        super().__init__(sender)
        self.action = action

    def __rich_repr__(self) -> RichReprResult:
        yield "action", self.action


class Resize(Event):
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


class Mount(Event):
    pass


class Unmount(Event):
    pass


class InputEvent(Event, bubble=True):
    pass


@rich_repr
class Key(InputEvent, bubble=True):
    __slots__ = ["key"]

    def __init__(self, sender: MessageTarget, key: Keys | str) -> None:
        super().__init__(sender)
        self.key = key.value if isinstance(key, Keys) else key

    def __rich_repr__(self) -> RichReprResult:
        yield "key", self.key


@rich_repr
class MouseEvent(InputEvent):
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
        screen_x: int | None = None,
        screen_y: int | None = None,
    ) -> None:
        super().__init__(sender)
        self.x = x
        self.y = y
        self.button = button
        self.shift = shift
        self.meta = meta
        self.ctrl = ctrl
        self.screen_x = x if screen_x is None else screen_x
        self.screen_y = y if screen_y is None else screen_y

    def __rich_repr__(self) -> RichReprResult:
        yield "x", self.x
        yield "y", self.y
        if self.screen_x != self.x:
            yield "screen_x", self.screen_x
        if self.screen_y != self.y:
            yield "screen_y", self.screen_y
        yield "button", self.button, 0
        yield "shift", self.shift, False
        yield "meta", self.meta, False
        yield "ctrl", self.ctrl, False

    def offset(self, x: int, y: int):
        return self.__class__(
            self.sender,
            x=self.x + x,
            y=self.y + y,
            button=self.button,
            shift=self.shift,
            meta=self.meta,
            ctrl=self.ctrl,
            screen_x=self.screen_x,
            screen_y=self.screen_y,
        )


@rich_repr
class MouseMove(MouseEvent):
    pass


@rich_repr
class MouseDown(MouseEvent):
    pass


@rich_repr
class MouseUp(MouseEvent):
    pass


class MouseScrollDown(InputEvent, bubble=True):
    __slots__ = ["x", "y"]

    def __init__(self, sender: MessageTarget, x: int, y: int) -> None:
        super().__init__(sender)
        self.x = x
        self.y = y


class MouseScrollUp(MouseScrollDown, bubble=True):
    pass


class Click(MouseEvent):
    pass


class DoubleClick(MouseEvent):
    pass


@rich_repr
class Timer(Event):
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


class Enter(Event):
    pass


class Leave(Event):
    pass


class Focus(Event):
    pass


class Blur(Event):
    pass


class Update(Event):
    def can_batch(self, event: Message) -> bool:
        return isinstance(event, Update) and event.sender == self.sender
