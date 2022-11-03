from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Type, TypeVar

import rich.repr
from rich.style import Style

from ._types import MessageTarget
from .geometry import Offset, Size
from .keys import _get_key_aliases
from .message import Message

MouseEventT = TypeVar("MouseEventT", bound="MouseEvent")

if TYPE_CHECKING:
    from .timer import Timer as TimerClass
    from .timer import TimerCallback
    from .widget import Widget


@rich.repr.auto
class Event(Message):
    """The base class for all events."""

    def __rich_repr__(self) -> rich.repr.Result:
        yield from ()


@rich.repr.auto
class Callback(Event, bubble=False, verbose=True):
    def __init__(
        self, sender: MessageTarget, callback: Callable[[], Awaitable[None]]
    ) -> None:
        self.callback = callback
        super().__init__(sender)

    def __rich_repr__(self) -> rich.repr.Result:
        yield "callback", self.callback


class InvokeCallbacks(Event, bubble=False, verbose=True):
    """Sent after the Screen is updated"""


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


class Resize(Event, bubble=False):
    """Sent when the app or widget has been resized.
    Args:
        sender (MessageTarget): The sender of the event (the Screen).
        size (Size): The new size of the Widget.
        virtual_size (Size): The virtual size (scrollable size) of the Widget.
        container_size (Size | None, optional): The size of the Widget's container widget. Defaults to None.

    """

    __slots__ = ["size", "virtual_size", "container_size"]

    def __init__(
        self,
        sender: MessageTarget,
        size: Size,
        virtual_size: Size,
        container_size: Size | None = None,
    ) -> None:
        self.size = size
        self.virtual_size = virtual_size
        self.container_size = size if container_size is None else container_size
        super().__init__(sender)

    def can_replace(self, message: "Message") -> bool:
        return isinstance(message, Resize)

    def __rich_repr__(self) -> rich.repr.Result:
        yield "size", self.size
        yield "virtual_size", self.virtual_size
        yield "container_size", self.container_size, self.size


class Compose(Event, bubble=False, verbose=True):
    """Sent to a widget to request it to compose and mount children."""


class Mount(Event, bubble=False, verbose=False):
    """Sent when a widget is *mounted* and may receive messages."""


class Unmount(Mount, bubble=False, verbose=False):
    """Sent when a widget is unmounted and may not longer receive messages."""


class Remove(Event, bubble=False):
    """Sent to a widget to ask it to remove itself from the DOM."""

    def __init__(self, sender: MessageTarget, widget: Widget) -> None:
        self.widget = widget
        super().__init__(sender)


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

    When a mouse has been captured, all further mouse events will be sent to the capturing widget.


    Args:
        sender (MessageTarget): The sender of the event, (in this case the app).
        mouse_position (Point): The position of the mouse when captured.

    """

    def __init__(self, sender: MessageTarget, mouse_position: Offset) -> None:
        super().__init__(sender)
        self.mouse_position = mouse_position

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, self.mouse_position


@rich.repr.auto
class MouseRelease(Event, bubble=False):
    """Mouse has been released.

    Args:
        sender (MessageTarget): The sender of the event, (in this case the app).
        mouse_position (Point): The position of the mouse when released.
    """

    def __init__(self, sender: MessageTarget, mouse_position: Offset) -> None:
        super().__init__(sender)
        self.mouse_position = mouse_position

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, self.mouse_position


class InputEvent(Event):
    pass


@rich.repr.auto
class Key(InputEvent):
    """Sent when the user hits a key on the keyboard.

    Args:
        sender (MessageTarget): The sender of the event (the App).
        key (str): A key name (textual.keys.Keys).
        char (str | None, optional): A printable character or None if it is not printable.

    Attributes:
        key_aliases (list[str]): The aliases for the key, including the key itself
    """

    __slots__ = ["key", "char"]

    def __init__(self, sender: MessageTarget, key: str, char: str | None) -> None:
        super().__init__(sender)
        self.key = key
        self.char = (key if len(key) == 1 else None) if char is None else char
        self.key_aliases = [_normalize_key(alias) for alias in _get_key_aliases(key)]

    def __rich_repr__(self) -> rich.repr.Result:
        yield "key", self.key
        yield "char", self.char, None

    @property
    def key_name(self) -> str | None:
        """Name of a key suitable for use as a Python identifier."""
        return _normalize_key(self.key)

    @property
    def is_printable(self) -> bool:
        """Return True if the key is printable. Currently, we assume any key event that
        isn't defined in key bindings is printable.

        Returns:
            bool: True if the key is printable.
        """
        return False if self.char is None else self.char.isprintable()


def _normalize_key(key: str) -> str:
    """Convert the key string to a name suitable for use as a Python identifier."""
    return key.replace("+", "_")


@rich.repr.auto
class MouseEvent(InputEvent, bubble=True):
    """Sent in response to a mouse event.

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
    def offset(self) -> Offset:
        """The mouse coordinate as an offset.

        Returns:
            Offset: Mouse coordinate.

        """
        return Offset(self.x, self.y)

    @property
    def screen_offset(self) -> Offset:
        """Mouse coordinate relative to the screen.

        Returns:
            Offset: Mouse coordinate.
        """
        return Offset(self.screen_x, self.screen_y)

    @property
    def delta(self) -> Offset:
        """Mouse coordinate delta (change since last event).

        Returns:
            Offset: Mouse coordinate.

        """
        return Offset(self.delta_x, self.delta_y)

    @property
    def style(self) -> Style:
        """The (Rich) Style under the cursor."""
        return self._style or Style()

    @style.setter
    def style(self, style: Style) -> None:
        self._style = style

    def get_content_offset(self, widget: Widget) -> Offset | None:
        """Get offset within a widget's content area, or None if offset is not in content (i.e. padding or border).

        Args:
            widget (Widget): Widget receiving the event.

        Returns:
            Offset | None: An offset where the origin is at the top left of the content area.
        """
        if self.screen_offset not in widget.content_region:
            return None
        return self.offset - widget.gutter.top_left

    def _apply_offset(self, x: int, y: int) -> MouseEvent:
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
class MouseMove(MouseEvent, bubble=False, verbose=True):
    """Sent when the mouse cursor moves."""


@rich.repr.auto
class MouseDown(MouseEvent, bubble=True, verbose=True):
    pass


@rich.repr.auto
class MouseUp(MouseEvent, bubble=True, verbose=True):
    pass


class MouseScrollDown(InputEvent, bubble=True, verbose=True):
    __slots__ = ["x", "y"]

    def __init__(self, sender: MessageTarget, x: int, y: int) -> None:
        super().__init__(sender)
        self.x = x
        self.y = y


class MouseScrollUp(InputEvent, bubble=True, verbose=True):
    __slots__ = ["x", "y"]

    def __init__(self, sender: MessageTarget, x: int, y: int) -> None:
        super().__init__(sender)
        self.x = x
        self.y = y


class Click(MouseEvent, bubble=True):
    pass


@rich.repr.auto
class Timer(Event, bubble=False, verbose=True):
    __slots__ = ["time", "count", "callback"]

    def __init__(
        self,
        sender: MessageTarget,
        timer: "TimerClass",
        time: float,
        count: int = 0,
        callback: TimerCallback | None = None,
    ) -> None:
        super().__init__(sender)
        self.timer = timer
        self.time = time
        self.count = count
        self.callback = callback

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.timer.name
        yield "count", self.count


class Enter(Event, bubble=False, verbose=True):
    pass


class Leave(Event, bubble=False, verbose=True):
    pass


class Focus(Event, bubble=False):
    pass


class Blur(Event, bubble=False):
    pass


class DescendantFocus(Event, bubble=True, verbose=True):
    pass


class DescendantBlur(Event, bubble=True, verbose=True):
    pass


@rich.repr.auto
class Paste(Event, bubble=False):
    """Event containing text that was pasted into the Textual application.
    This event will only appear when running in a terminal emulator that supports
    bracketed paste mode. Textual will enable bracketed pastes when an app starts,
    and disable it when the app shuts down.

    Args:
        sender (MessageTarget): The sender of the event, (in this case the app).
        text: The text that has been pasted.
    """

    def __init__(self, sender: MessageTarget, text: str) -> None:
        super().__init__(sender)
        self.text = text

    def __rich_repr__(self) -> rich.repr.Result:
        yield "text", self.text


class ScreenResume(Event, bubble=False):
    pass


class ScreenSuspend(Event, bubble=False):
    pass
