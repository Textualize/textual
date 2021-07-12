from __future__ import annotations

from typing import Awaitable, Callable, Type, TYPE_CHECKING, TypeVar

import rich.repr
from rich.style import Style

from .geometry import Point, Dimensions
from .message import Message
from ._types import MessageTarget
from .keys import Keys


MouseEventT = TypeVar("MouseEventT", bound="MouseEvent")

if TYPE_CHECKING:
    from ._timer import Timer as TimerClass
    from ._timer import TimerCallback


@rich.repr.auto
class Event(Message):
    def __rich_repr__(self) -> rich.repr.RichReprResult:
        return
        yield

    def __init_subclass__(cls, bubble: bool = False) -> None:
        super().__init_subclass__(bubble=bubble)


class Null(Event):
    def can_replace(self, message: Message) -> bool:
        return isinstance(message, Null)


@rich.repr.auto
class Callback(Event, bubble=False):
    def __init__(
        self, sender: MessageTarget, callback: Callable[[], Awaitable]
    ) -> None:
        self.callback = callback
        super().__init__(sender)

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "callback", self.callback


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


class Action(Event, bubble=True):
    __slots__ = ["action"]

    def __init__(self, sender: MessageTarget, action: str) -> None:
        super().__init__(sender)
        self.action = action

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "action", self.action


class Resize(Event):
    __slots__ = ["width", "height"]
    width: int
    height: int

    def __init__(self, sender: MessageTarget, width: int, height: int) -> None:
        self.width = width
        self.height = height
        super().__init__(sender)

    def can_replace(self, message: "Message") -> bool:
        return isinstance(message, Resize)

    @property
    def size(self) -> Dimensions:
        return Dimensions(self.width, self.height)

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield self.width
        yield self.height


class Mount(Event):
    pass


class Unmount(Event):
    pass


class Show(Event):
    """Widget has become visible."""


class Hide(Event):
    """Widget has been hidden."""


@rich.repr.auto
class MouseCaptured(Event):
    """Mouse has been captured."""

    def __init__(self, sender: MessageTarget, mouse_position: Point) -> None:
        super().__init__(sender)
        self.mouse_position = mouse_position

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield None, self.mouse_position


@rich.repr.auto
class MouseReleased(Event):
    """Mouse has been released."""

    def __init__(self, sender: MessageTarget, mouse_position: Point) -> None:
        super().__init__(sender)
        self.mouse_position = mouse_position

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield None, self.mouse_position


class InputEvent(Event, bubble=True):
    pass


@rich.repr.auto
class Key(InputEvent, bubble=True):
    __slots__ = ["key"]

    def __init__(self, sender: MessageTarget, key: Keys | str) -> None:
        super().__init__(sender)
        self.key = key.value if isinstance(key, Keys) else key

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "key", self.key


@rich.repr.auto
class MouseEvent(InputEvent):
    __slots__ = ["x", "y", "button"]

    def __init__(
        self,
        sender: MessageTarget,
        x: int,
        y: int,
        delta_x: int,
        delta_y: int,
        button: int,
        shift: bool,
        meta: bool,
        ctrl: bool,
        screen_x: int | None = None,
        screen_y: int | None = None,
        style: Style | None = None,
    ) -> None:
        super().__init__(sender)
        self.x = x
        self.y = y
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.button = button
        self.shift = shift
        self.meta = meta
        self.ctrl = ctrl
        self.screen_x = x if screen_x is None else screen_x
        self.screen_y = y if screen_y is None else screen_y
        self._style = style or Style()

    @classmethod
    def from_event(cls: Type[MouseEventT], event: MouseEvent) -> MouseEventT:
        new_event = cls(
            event.sender,
            event.x,
            event.y,
            event.delta_x,
            event.delta_y,
            event.button,
            event.shift,
            event.meta,
            event.ctrl,
            event.screen_x,
            event.screen_y,
            event._style,
        )
        return new_event

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "x", self.x
        yield "y", self.y
        yield "delta_x", self.delta_x, 0
        yield "delta_y", self.delta_y, 0
        if self.screen_x != self.x:
            yield "screen_x", self.screen_x
        if self.screen_y != self.y:
            yield "screen_y", self.screen_y
        yield "button", self.button, 0
        yield "shift", self.shift, False
        yield "meta", self.meta, False
        yield "ctrl", self.ctrl, False

    @property
    def style(self) -> Style:
        return self._style or Style()

    @style.setter
    def style(self, style: Style) -> None:
        self._style = style

    def offset(self, x: int, y: int) -> MouseEvent:
        return self.__class__(
            self.sender,
            x=self.x + x,
            y=self.y + y,
            delta_x=self.delta_x,
            delta_y=self.delta_y,
            button=self.button,
            shift=self.shift,
            meta=self.meta,
            ctrl=self.ctrl,
            screen_x=self.screen_x,
            screen_y=self.screen_y,
            style=self.style,
        )


@rich.repr.auto
class MouseMove(MouseEvent):
    pass


@rich.repr.auto
class MouseDown(MouseEvent):
    pass


@rich.repr.auto
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


@rich.repr.auto
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

    def __rich_repr__(self) -> rich.repr.RichReprResult:
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
    def can_replace(self, event: Message) -> bool:
        return isinstance(event, Update) and event.sender == self.sender
