from __future__ import annotations

from typing import Awaitable, Callable, Type, TYPE_CHECKING, TypeVar

import rich.repr
from rich.style import Style

from .geometry import Offset, Size
from .message import Message
from ._types import MessageTarget
from .keys import Keys

MouseEventT = TypeVar("MouseEventT", bound="MouseEvent")

if TYPE_CHECKING:
    from ._timer import Timer as TimerClass
    from ._timer import TimerCallback


@rich.repr.auto
class Event(Message):
    def __rich_repr__(self) -> rich.repr.Result:
        return
        yield

    def __init_subclass__(cls, bubble: bool = True, verbosity: int = 1) -> None:
        super().__init_subclass__(bubble=bubble, verbosity=verbosity)


class Null(Event, verbosity=3):
    def can_replace(self, message: Message) -> bool:
        return isinstance(message, Null)


@rich.repr.auto
class Callback(Event, bubble=False, verbosity=3):
    def __init__(
        self, sender: MessageTarget, callback: Callable[[], Awaitable[None]]
    ) -> None:
        self.callback = callback
        super().__init__(sender)

    def __rich_repr__(self) -> rich.repr.Result:
        yield "callback", self.callback


class ShutdownRequest(Event):
    pass


class Shutdown(Event):
    pass


class Load(Event, bubble=False):
    """
    Sent when the App is running but *before* the terminal is in application mode.

    Use this event to run any set up that doesn't require any visuals such as loading
    configuration and binding keys.


    """


class Idle(Event, bubble=False):
    """Sent when there are no more items in the message queue.

    This is a pseudo-event in that it is created by the Textual system and doesn't go
    through the usual message queue.

    """


class Action(Event):
    __slots__ = ["action"]

    def __init__(self, sender: MessageTarget, action: str) -> None:
        super().__init__(sender)
        self.action = action

    def __rich_repr__(self) -> rich.repr.Result:
        yield "action", self.action


class Resize(Event, verbosity=2, bubble=False):
    """Sent when the app or widget has been resized."""

    __slots__ = ["size"]
    size: Size

    def __init__(self, sender: MessageTarget, size: Size) -> None:
        """
        Args:
            sender (MessageTarget): Event sender.
            width (int): New width in terminal cells.
            height (int): New height in terminal cells.
        """
        self.size = size
        super().__init__(sender)

    def can_replace(self, message: "Message") -> bool:
        return isinstance(message, Resize)

    @property
    def width(self) -> int:
        return self.size.width

    @property
    def height(self) -> int:
        return self.size.height

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.width
        yield self.height


class Mount(Event, bubble=False):
    """Sent when a widget is *mounted* and may receive messages."""


class Unmount(Event, bubble=False):
    """Sent when a widget is unmounted, and may no longer receive messages."""


class Show(Event, bubble=False):
    """Sent when a widget has become visible."""


class Hide(Event, bubble=False):
    """Sent when a widget has been hidden.

    A widget may be hidden by setting its `visible` flag to `False`, if it is no longer in a layout,
    or if it has been offset beyond the edges of the terminal.

    """


@rich.repr.auto
class MouseCapture(Event, bubble=False):
    """Sent when the mouse has been captured.

    When a mouse has been captures, all further mouse events will be sent to the capturing widget.

    """

    def __init__(self, sender: MessageTarget, mouse_position: Offset) -> None:
        """

        Args:
            sender (MessageTarget): The sender of the event, (in this case the app).
            mouse_position (Point): The position of the mouse when captured.
        """
        super().__init__(sender)
        self.mouse_position = mouse_position

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, self.mouse_position


@rich.repr.auto
class MouseRelease(Event, bubble=False):
    """Mouse has been released."""

    def __init__(self, sender: MessageTarget, mouse_position: Offset) -> None:
        """
        Args:
            sender (MessageTarget): The sender of the event, (in this case the app).
            mouse_position (Point): The position of the mouse when released.
        """
        super().__init__(sender)
        self.mouse_position = mouse_position

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, self.mouse_position


class InputEvent(Event):
    pass


@rich.repr.auto
class Key(InputEvent):
    """Sent when the user hits a key on the keyboard"""

    __slots__ = ["key"]

    def __init__(self, sender: MessageTarget, key: str) -> None:
        """

        Args:
            sender (MessageTarget): The sender of the event (the App)
            key (str): The pressed key if a single character (or a longer string for special characters)
        """
        super().__init__(sender)
        self.key = key.value if isinstance(key, Keys) else key

    def __rich_repr__(self) -> rich.repr.Result:
        yield "key", self.key


@rich.repr.auto
class MouseEvent(InputEvent, bubble=True):
    """Sent in response to a mouse event"""

    __slots__ = [
        "x",
        "y",
        "delta_x",
        "delta_y",
        "button",
        "shift",
        "meta",
        "ctrl",
        "screen_x",
        "screen_y",
        "_style",
    ]

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
        """

        Args:
            sender (MessageTarget): The sender of the event.
            x (int): The relative x coordinate.
            y (int): The relative y coordinate.
            delta_x (int): Change in x since the last message.
            delta_y (int): Change in y since the last message.
            button (int): Indexed of the pressed button.
            shift (bool): True if the shift key is pressed.
            meta (bool): True if the meta key is pressed.
            ctrl (bool): True if the ctrl key is pressed.
            screen_x (int, optional): The absolute x coordinate.
            screen_y (int, optional): The absolute y coordinate.
            style (Style, optional): The Rich Style under the mouse cursor.
        """
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

    def __rich_repr__(self) -> rich.repr.Result:
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
class MouseMove(MouseEvent, verbosity=3, bubble=True):
    """Sent when the mouse cursor moves."""


@rich.repr.auto
class MouseDown(MouseEvent, bubble=True):
    pass


@rich.repr.auto
class MouseUp(MouseEvent, bubble=True):
    pass


class MouseScrollDown(InputEvent, verbosity=3, bubble=True):
    __slots__ = ["x", "y"]

    def __init__(self, sender: MessageTarget, x: int, y: int) -> None:
        super().__init__(sender)
        self.x = x
        self.y = y


class MouseScrollUp(MouseScrollDown, bubble=True):
    pass


class Click(MouseEvent, bubble=True):
    pass


class DoubleClick(MouseEvent, bubble=True):
    pass


@rich.repr.auto
class Timer(Event, verbosity=3, bubble=False):
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

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.timer.name
        yield "count", self.count


class Enter(Event, bubble=False):
    pass


class Leave(Event, bubble=False):
    pass


class Focus(Event, bubble=False):
    pass


class Blur(Event, bubble=False):
    pass


# class Update(Event, bubble=False):
#     def can_replace(self, event: Message) -> bool:
#         return isinstance(event, Update) and event.sender == self.sender
