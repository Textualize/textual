from __future__ import annotations

from functools import partial
from logging import getLogger
from typing import (
    Any,
    TYPE_CHECKING,
    Callable,
    ClassVar,
    NewType,
    cast,
)
from weakref import WeakValueDictionary

import rich.repr
from rich.align import Align
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.pretty import Pretty
from rich.style import Style

from . import events
from ._animator import BoundAnimator
from ._context import active_app
from .geometry import Dimensions
from .message import Message
from .message_pump import MessagePump
from .messages import LayoutMessage, UpdateMessage
from .reactive import Reactive, watch

if TYPE_CHECKING:
    from .app import App
    from .view import View


WidgetID = NewType("WidgetID", int)

log = getLogger("rich")


@rich.repr.auto
class Widget(MessagePump):
    _id: ClassVar[int] = 0
    _counts: ClassVar[dict[str, int]] = {}
    can_focus: bool = False

    def __init__(self, name: str | None = None) -> None:
        class_name = self.__class__.__name__
        Widget._counts.setdefault(class_name, 0)
        Widget._counts[class_name] += 1
        _count = self._counts[class_name]
        self.id: WidgetID = cast(WidgetID, Widget._id)
        Widget._id += 1

        self.name = name or f"{class_name}#{_count}"

        self.size = Dimensions(0, 0)
        self.size_changed = False
        self._repaint_required = False
        self._layout_required = False
        self._animate: BoundAnimator | None = None
        self._reactive_watches: dict[str, Callable] = {}

        super().__init__()

    visible: Reactive[bool] = Reactive(True, layout=True)
    layout_size: Reactive[int | None] = Reactive(None)
    layout_fraction: Reactive[int] = Reactive(1)
    layout_min_size: Reactive[int] = Reactive(1)
    layout_offset_x: Reactive[float] = Reactive(0, layout=True)
    layout_offset_y: Reactive[float] = Reactive(0, layout=True)

    def __init_subclass__(cls, can_focus: bool = True) -> None:
        super().__init_subclass__()
        cls.can_focus = can_focus

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "name", self.name

    def __rich__(self) -> RenderableType:
        return self.render()

    def watch(self, attribute_name, callback: Callable[[Any], None]) -> None:
        watch(self, attribute_name, callback)

    @property
    def is_visual(self) -> bool:
        return True

    @property
    def app(self) -> "App":
        """Get the current app."""
        return active_app.get()

    @property
    def console(self) -> Console:
        """Get the current console."""
        return active_app.get().console

    @property
    def root_view(self) -> "View":
        """Return the top-most view."""
        return active_app.get().view

    @property
    def animate(self) -> BoundAnimator:
        if self._animate is None:
            self._animate = self.app.animator.bind(self)
        assert self._animate is not None
        return self._animate

    @property
    def layout_offset(self) -> tuple[int, int]:
        """Get the layout offset as a tuple."""
        return (round(self.layout_offset_x), round(self.layout_offset_y))

    def require_repaint(self) -> None:
        """Mark widget as requiring a repaint.

        Actual repaint is done by parent on idle.
        """
        self._repaint_required = True
        self.post_message_no_wait(events.Null(self))

    def require_layout(self) -> None:
        self._layout_required = True
        self.post_message_no_wait(events.Null(self))

    def check_repaint(self) -> bool:
        return self._repaint_required

    def check_layout(self) -> bool:
        return self._layout_required

    def reset_check_repaint(self) -> None:
        self._repaint_required = False

    def reset_check_layout(self) -> None:
        self._layout_required = False

    def get_style_at(self, x: int, y: int) -> Style:
        offset_x, offset_y = self.root_view.get_offset(self)
        return self.root_view.get_style_at(x + offset_x, y + offset_y)

    async def call_later(self, callback: Callable, *args, **kwargs) -> None:
        await self.app.call_later(callback, *args, **kwargs)

    async def forward_event(self, event: events.Event) -> None:
        await self.post_message(event)

    async def refresh(self) -> None:
        """Re-render the window and repaint it."""
        self.require_repaint()
        await self.repaint()

    async def repaint(self) -> None:
        """Instructs parent to repaint this widget."""
        await self.emit(UpdateMessage(self, self))

    async def update_layout(self) -> None:
        await self.emit(LayoutMessage(self))

    def render(self) -> RenderableType:
        """Get renderable for widget.

        Returns:
            RenderableType: Any renderable
        """
        return Panel(
            Align.center(Pretty(self), vertical="middle"), title=self.__class__.__name__
        )

    async def action(self, action: str, *params) -> None:
        await self.app.action(action, self)

    async def post_message(self, message: Message) -> bool:
        if not self.check_message_enabled(message):
            return True
        return await super().post_message(message)

    async def on_event(self, event: events.Event) -> None:
        if isinstance(event, events.Resize):
            new_size = Dimensions(event.width, event.height)
            if self.size != new_size:
                self.size = new_size
                self.require_repaint()
        await super().on_event(event)

    async def on_idle(self, event: events.Idle) -> None:
        if self.check_layout():
            self.reset_check_repaint()
            self.reset_check_layout()
            await self.update_layout()
        elif self.check_repaint():
            self.reset_check_repaint()
            self.reset_check_layout()
            await self.repaint()

    async def focus(self) -> None:
        await self.app.set_focus(self)

    async def capture_mouse(self, capture: bool = True) -> None:
        await self.app.capture_mouse(self if capture else None)

    async def release_mouse(self) -> None:
        await self.app.capture_mouse(None)

    async def broker_event(self, event_name: str, event: events.Event) -> bool:
        return await self.app.broker_event(event_name, event, default_namespace=self)

    async def dispatch_key(self, event: events.Key) -> None:
        """Dispatch a key event to method.

        This method will call the method named 'key_<event.key>' if it exists.

        Args:
            event (events.Key): A key event.
        """

        key_method = getattr(self, f"key_{event.key}", None)
        if key_method is not None:
            await key_method()

    async def on_mouse_down(self, event: events.MouseUp) -> None:
        await self.broker_event("mouse.down", event)

    async def on_mouse_up(self, event: events.MouseUp) -> None:
        await self.broker_event("mouse.up", event)

    async def on_click(self, event: events.Click) -> None:
        await self.broker_event("click", event)
