from __future__ import annotations

from logging import getLogger
from typing import (
    Callable,
    ClassVar,
    Generic,
    Iterable,
    NamedTuple,
    TypeVar,
    TYPE_CHECKING,
)

from rich.align import Align

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.pretty import Pretty
from rich.panel import Panel
from rich.repr import rich_repr, RichReprResult
from rich.segment import Segment

from . import events
from ._context import active_app
from ._line_cache import LineCache
from .message import Message
from .message_pump import MessagePump
from .geometry import Dimensions

from time import time

if TYPE_CHECKING:
    from .app import App

log = getLogger("rich")

T = TypeVar("T")


class UpdateMessage(Message):
    def can_batch(self, message: Message) -> bool:
        return isinstance(message, UpdateMessage) and message.sender == self.sender


class Reactive(Generic[T]):
    def __init__(
        self, default: T, validator: Callable[[object, T], T] | None = None
    ) -> None:
        self._default = default
        self.validator = validator

    def __set_name__(self, owner: "Widget", name: str) -> None:
        self.internal_name = f"_{name}"
        setattr(owner, self.internal_name, self._default)

    def __get__(self, obj: "Widget", obj_type: type[object]) -> T:
        return getattr(obj, self.internal_name)

    def __set__(self, obj: "Widget", value: T) -> None:
        if getattr(obj, self.internal_name) != value:
            log.debug("%s -> %s", self.internal_name, value)
            if self.validator:
                value = self.validator(obj, value)
            setattr(obj, self.internal_name, value)
            obj.require_repaint()


class Widget(MessagePump):
    _count: ClassVar[int] = 0
    can_focus: bool = False

    def __init__(self, name: str | None = None) -> None:
        self.name = name or f"{self.__class__.__name__}#{self._count}"
        Widget._count += 1
        self.size = Dimensions(0, 0)
        self.size_changed = False
        self._repaint_required = False
        self._line_cache: LineCache = LineCache()

        super().__init__()
        self.disable_messages(events.MouseMove)

    def __init_subclass__(
        cls,
        can_focus: bool = True,
    ) -> None:
        super().__init_subclass__()
        cls.can_focus = can_focus

    def __rich_repr__(self) -> RichReprResult:
        yield "name", self.name

    @property
    def app(self) -> "App":
        """Get the current app."""
        return active_app.get()

    @property
    def console(self) -> Console:
        """Get the current console."""
        try:
            return active_app.get().console
        except LookupError:
            return Console()

    # def __rich__(self) -> LineCache:
    #     return self.line_cache

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        renderable = self.render(console, options)
        self._line_cache.update(console, options, renderable)
        yield self._line_cache

    def require_repaint(self) -> None:
        self._repaint_required = True

    async def forward_event(self, event: events.Event) -> None:
        await self.post_message(event)

    async def refresh(self) -> None:
        self._repaint_required = True
        await self.repaint()

    async def repaint(self) -> None:
        await self.emit(UpdateMessage(self))

    def render_update(self, x: int, y: int) -> Iterable[Segment]:
        width, height = self.size
        yield from self.line_cache.render(x, y, width, height)

    def render(self, console: Console, options: ConsoleOptions) -> RenderableType:
        return Panel(
            Align.center(Pretty(self), vertical="middle"), title=self.__class__.__name__
        )

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
        if self.line_cache is None or self.line_cache.dirty:
            await self.repaint()
