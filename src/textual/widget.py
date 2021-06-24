from __future__ import annotations

from logging import getLogger
from typing import (
    Callable,
    ClassVar,
    Generic,
    Iterable,
    TypeVar,
    TYPE_CHECKING,
)

from rich.align import Align

from rich.console import Console, RenderableType
from rich.pretty import Pretty
from rich.panel import Panel
import rich.repr
from rich.segment import Segment
from rich.style import Style

from . import events
from ._animator import BoundAnimator
from ._context import active_app
from ._loop import loop_last
from ._line_cache import LineCache
from .message import Message
from .message_pump import MessagePump
from .geometry import Dimensions

from time import time

if TYPE_CHECKING:
    from .app import App

log = getLogger("rich")


@rich.repr.auto
class UpdateMessage(Message):
    def __init__(
        self,
        sender: MessagePump,
        widget: WidgetBase,
        offset_x: int = 0,
        offset_y: int = 0,
    ):
        super().__init__(sender)
        self.widget = widget
        self.offset_x = offset_x
        self.offset_y = offset_y

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield self.sender
        yield "widget"
        yield "offset_x", self.offset_x, 0
        yield "offset_y", self.offset_y, 0

    def can_batch(self, message: Message) -> bool:
        return isinstance(message, UpdateMessage) and message.sender == self.sender


ReactiveType = TypeVar("ReactiveType")


class Reactive(Generic[ReactiveType]):
    def __init__(
        self,
        default: ReactiveType,
        validator: Callable[[object, ReactiveType], ReactiveType] | None = None,
    ) -> None:
        self._default = default
        self.validator = validator

    def __set_name__(self, owner: "WidgetBase", name: str) -> None:
        self.name = name
        self.internal_name = f"__{name}"
        setattr(owner, self.internal_name, self._default)

    def __get__(self, obj: "WidgetBase", obj_type: type[object]) -> ReactiveType:
        return getattr(obj, self.internal_name)

    def __set__(self, obj: "WidgetBase", value: ReactiveType) -> None:
        if getattr(obj, self.internal_name) != value:

            current_value = getattr(obj, self.internal_name, None)
            validate_function = getattr(obj, f"validate_{self.name}", None)
            if callable(validate_function):
                value = validate_function(value)

            if current_value != value:
                setattr(obj, self.internal_name, value)

                update_function = getattr(obj, f"update_{self.name}", None)
                if callable(update_function):
                    update_function(current_value, value)

                obj.require_repaint()
                # obj.post_message_no_wait(events.Null(obj))


@rich.repr.auto
class WidgetBase(MessagePump):
    _counts: ClassVar[dict[str, int]] = {}
    can_focus: bool = False

    def __init__(self, name: str | None = None) -> None:
        Widget._counts.setdefault(self.__class__.__name__, 1)
        _count = self._counts[self.__class__.__name__]
        self.name = name or f"{self.__class__.__name__}#{_count}"

        self.size = Dimensions(0, 0)
        self.size_changed = False
        self._repaint_required = False
        self._animate: BoundAnimator | None = None

        super().__init__()
        # self.disable_messages(events.MouseMove)

    def __init_subclass__(
        cls,
        can_focus: bool = True,
    ) -> None:
        super().__init_subclass__()
        cls.can_focus = can_focus

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "name", self.name

    def __rich__(self) -> RenderableType:
        return self.render()

    @property
    def app(self) -> "App":
        """Get the current app."""
        return active_app.get()

    @property
    def console(self) -> Console:
        """Get the current console."""
        return active_app.get().console

    @property
    def animate(self) -> BoundAnimator:
        if self._animate is None:
            self._animate = self.app.animator.bind(self)
        assert self._animate is not None
        return self._animate

    def require_repaint(self) -> None:
        """Mark widget as requiring a repaint.

        Actual repaint is done by parent on idle.
        """
        self._repaint_required = True
        self.post_message_no_wait(events.Null(self))

    def check_repaint(self) -> bool:
        return True
        return self._repaint_required

    async def forward_event(self, event: events.Event) -> None:
        await self.post_message(event)

    async def refresh(self) -> None:
        """Re-render the window and repaint it."""
        self.require_repaint()
        await self.repaint()

    async def repaint(self) -> None:
        """Instructs parent to repaint this widget."""
        await self.emit(UpdateMessage(self, self))

    def render_update(self, x: int, y: int) -> Iterable[Segment]:
        """Render an update to a portion of the screen.

        Args:
            x (int): X offset from origin.
            y (int): Y offset form origin.

        Returns:
            Iterable[Segment]: Partial update.
        """
        return

        width, height = self.size
        lines = self.console.render_lines(
            self.render(), self.console.options.update_dimensions(width, height)
        )

        new_line = Segment.line()
        for last, line in loop_last(lines):
            yield from line
            if not last:
                yield new_line

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
        if self.check_repaint():
            await self.repaint()


class Widget(WidgetBase):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._line_cache: LineCache | None = None

    @property
    def line_cache(self) -> LineCache:

        if self._line_cache is None:
            width, height = self.size
            start = time()
            try:
                renderable = self.render()
            except Exception:
                log.exception("error in render")
                raise
            self._line_cache = LineCache.from_renderable(
                self.console, renderable, width, height
            )
        assert self._line_cache is not None
        return self._line_cache

    # def __rich__(self) -> LineCache:
    #     return self.line_cache

    async def focus(self) -> None:
        await self.app.set_focus(self)

    def get_style_at(self, x: int, y: int) -> Style:
        return self.line_cache.get_style_at(x, y)

    def render(self) -> RenderableType:
        raise NotImplementedError
        # return self.line_cache

    def require_repaint(self) -> None:
        self._line_cache = None
        super().require_repaint()

    def check_repaint(self) -> bool:
        return self._line_cache is None or self.line_cache.dirty

    def render_update(self, x: int, y: int) -> Iterable[Segment]:
        """Render an update to a portion of the screen.

        Args:
            x (int): X offset from origin.
            y (int): Y offset form origin.

        Returns:
            Iterable[Segment]: Partial update.
        """
        width, height = self.size
        yield from self.line_cache.render(x, y, width, height)

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        style_under_cursor = self.get_style_at(event.x, event.y)
        if style_under_cursor:
            log.debug("%r", style_under_cursor)

    async def on_mouse_up(self, event: events.MouseUp) -> None:
        style = self.get_style_at(event.x, event.y)
        if "@click" in style.meta:
            log.debug(style._link_id)
            await self.app.action(style.meta["@click"])


class StaticWidget(Widget):
    def __init__(self, renderable: RenderableType, name: str | None = None) -> None:
        super().__init__(name)
        self.renderable = renderable

    def render(self) -> RenderableType:
        return self.renderable