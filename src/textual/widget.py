from __future__ import annotations

from logging import getLogger
from typing import (
    Any,
    Awaitable,
    TYPE_CHECKING,
    Callable,
    ClassVar,
    NamedTuple,
    NewType,
    cast,
)
import rich.repr
from rich.align import Align
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.pretty import Pretty
from rich.segment import Segment
from rich.style import Style

from . import events
from ._animator import BoundAnimator
from ._context import active_app
from .geometry import Size
from .message import Message
from .message_pump import MessagePump
from .messages import LayoutMessage, UpdateMessage
from .reactive import Reactive, watch
from ._types import Lines

if TYPE_CHECKING:
    from .app import App
    from .view import View

log = getLogger("rich")


class RenderCache(NamedTuple):
    size: Size
    lines: Lines


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

        self.name = name or f"{class_name}#{_count}"

        self._size = Size(0, 0)
        self._repaint_required = False
        self._layout_required = False
        self._animate: BoundAnimator | None = None
        self._reactive_watches: dict[str, Callable] = {}
        self.render_cache: RenderCache | None = None
        self.highlight_style: Style | None = None

        super().__init__()

    visible: Reactive[bool] = Reactive(True, layout=True)
    layout_size: Reactive[int | None] = Reactive(None, layout=True)
    layout_fraction: Reactive[int] = Reactive(1, layout=True)
    layout_min_size: Reactive[int] = Reactive(1, layout=True)
    layout_offset_x: Reactive[float] = Reactive(0.0, layout=True)
    layout_offset_y: Reactive[float] = Reactive(0.0, layout=True)

    def validate_layout_offset_x(self, value) -> int:
        return int(value)

    def validate_layout_offset_y(self, value) -> int:
        return int(value)

    def __init_subclass__(cls, can_focus: bool = True) -> None:
        super().__init_subclass__()
        cls.can_focus = can_focus

    def __rich_repr__(self) -> rich.repr.Result:
        yield "name", self.name

    def __rich__(self) -> RenderableType:
        return self.render()

    def watch(self, attribute_name, callback: Callable[[Any], Awaitable[None]]) -> None:
        watch(self, attribute_name, callback)

    @property
    def size(self) -> Size:
        return self._size

    @property
    def is_visual(self) -> bool:
        return True

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

    def _update_size(self, size: Size) -> None:
        self._size = size

    def render_lines(self) -> RenderCache:
        width, height = self.size
        renderable = self.render()
        options = self.console.options.update_dimensions(width, height)
        lines = self.console.render_lines(renderable, options)
        self.render_cache = RenderCache(self.size, lines)
        return self.render_cache

    def render_lines_free(self, width: int) -> RenderCache:

        renderable = self.render()

        options = self.console.options.update(width=width, height=None)

        lines = self.console.render_lines(renderable, options)
        self.render_cache = RenderCache(Size(width, len(lines)), lines)
        return self.render_cache

    def _get_lines(self) -> Lines:
        """Get render lines for given dimensions.

        Args:
            width (int): [description]
            height (int): [description]

        Returns:
            Lines: [description]
        """
        if self.render_cache is None:
            self.render_cache = self.render_lines()
        lines = self.render_cache.lines
        return lines

    def clear_render_cache(self) -> None:
        self.render_cache = None

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

    def refresh(self, repaint: bool = True, layout: bool = False) -> None:
        """Initiate a refresh of the widget.

        This method sets an internal flag to perform a refresh, which will be done on the
        next idle event. Only one refresh will be done even if this method is called multiple times.

        Args:
            repaint (bool, optional): Repaint the widget (will call render() again). Defaults to True.
            layout (bool, optional): Also layout widgets in the view. Defaults to False.
        """
        if layout:
            self.clear_render_cache()
            self._layout_required = True
        elif repaint:
            self.clear_render_cache()
            self._repaint_required = True
        self.post_message_no_wait(events.Null(self))

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
        if not self.is_running:
            self.log(self, "IS NOT RUNNING")
        return await super().post_message(message)

    async def on_resize(self, event: events.Resize) -> None:
        self.refresh()

    async def on_idle(self, event: events.Idle) -> None:
        if self.check_layout():
            self.reset_check_repaint()
            self.reset_check_layout()
            await self.emit(LayoutMessage(self))
        elif self.check_repaint():
            self.render_cache = None
            self.reset_check_repaint()
            await self.emit(UpdateMessage(self, self, layout=False))

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
