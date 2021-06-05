from logging import getLogger
from typing import (
    ClassVar,
    Generic,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Type,
    TypeVar,
    TYPE_CHECKING,
)

from rich.align import Align
from rich import box
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.pretty import Pretty
from rich.panel import Panel
from rich.repr import rich_repr, RichReprResult
from rich.segment import Segment

from . import events
from ._context import active_app
from ._line_cache import LineCache
from .message import Message
from .message_pump import MessagePump

if TYPE_CHECKING:
    from .app import App

log = getLogger("rich")

T = TypeVar("T")


class Reactive(Generic[T]):
    def __init__(self, default: T) -> None:
        self._default = default

    def __set_name__(self, owner: "Widget", name: str) -> None:
        self.internal_name = f"_{name}"
        setattr(owner, self.internal_name, self._default)

    def __get__(self, obj: "Widget", obj_type: Type[object]) -> T:
        return getattr(obj, self.internal_name)

    def __set__(self, obj: "Widget", value: T) -> None:
        if getattr(obj, self.internal_name) != value:
            log.debug("%s -> %s", self.internal_name, value)
            setattr(obj, self.internal_name, value)
            obj.require_refresh()


class WidgetDimensions(NamedTuple):
    width: int
    height: int


@rich_repr
class Widget(MessagePump):
    _count: ClassVar[int] = 0
    can_focus: bool = False
    mouse_events: bool = False
    idle_events: bool = False

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name or f"{self.__class__.__name__}#{self._count}"
        Widget._count += 1
        self.size = WidgetDimensions(0, 0)
        self.size_changed = False
        self._refresh_required = False
        self._line_cache: Optional[LineCache] = None
        super().__init__()
        if not self.mouse_events:
            self.disable_messages(
                events.Move,
                events.Press,
                events.Release,
                events.Click,
                events.DoubleClick,
            )
        if not self.idle_events:
            self.disable_messages(events.Idle)

    def __init_subclass__(
        cls,
        can_focus: bool = False,
        mouse_events: bool = True,
        idle_events: bool = False,
    ) -> None:
        super().__init_subclass__()
        cls.can_focus = can_focus
        cls.mouse_events = mouse_events
        cls.idle_events = idle_events

    has_focus: Reactive[bool] = Reactive(False)
    mouse_over: Reactive[bool] = Reactive(False)

    def __rich_repr__(self) -> RichReprResult:
        yield "name", self.name

    @property
    def app(self) -> "App":
        """Get the current app."""
        return active_app.get()

    @property
    def console(self) -> Console:
        """Get the current console."""
        return active_app.get().console

    @property
    def line_cache(self) -> LineCache:

        if self._line_cache is None:
            width, height = self.size
            renderable = self.render()
            self._line_cache = LineCache.from_renderable(
                self.console, renderable, width, height
            )
        assert self._line_cache is not None
        return self._line_cache

    def __rich__(self) -> LineCache:
        return self.line_cache

    def require_refresh(self) -> None:
        self._line_cache = None

    def render_update(self, x: int, y: int) -> Iterable[Segment]:
        yield from self.line_cache.render(x, y)

    def render(self) -> RenderableType:
        return Panel(
            Align.center(Pretty(self), vertical="middle"),
            title=self.__class__.__name__,
            border_style="green" if self.mouse_over else "blue",
            box=box.HEAVY if self.has_focus else box.ROUNDED,
        )

    async def post_message(
        self, message: Message, priority: Optional[int] = None
    ) -> bool:
        if not self.check_message_enabled(message):
            return True
        log.debug("%r -> %s", message, self.name)
        return await super().post_message(message, priority)

    async def on_event(self, event: events.Event, priority: int) -> None:
        if isinstance(event, (events.Enter, events.Leave)):
            self.mouse_over = isinstance(event, events.Enter)
        await super().on_event(event, priority)

    async def on_resize(self, event: events.Resize) -> None:
        new_size = WidgetDimensions(event.width, event.height)
        if self.size != new_size:
            self.size = new_size
            self.require_refresh()

    async def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True

    async def on_blur(self, event: events.Focus) -> None:
        self.has_focus = False

    async def on_idle(self, event: events.Idle) -> None:
        self.app.refresh()
