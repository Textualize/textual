from logging import getLogger
from typing import ClassVar, NamedTuple, Optional, TYPE_CHECKING


from rich.align import Align
from rich import box
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.pretty import Pretty
from rich.panel import Panel
from rich.repr import rich_repr, RichReprResult

from . import events
from ._context import active_app
from .message import Message
from .message_pump import MessagePump

if TYPE_CHECKING:
    from .app import App

log = getLogger("rich")


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
        self._has_focus = False
        self._mouse_over = False
        super().__init__()
        if not self.mouse_events:
            self.disable_messages(events.MouseMove)
        if not self.idle_events:
            self.disable_messages(events.Idle)

    def __init_subclass__(cls, can_focus: bool = True) -> None:
        super().__init_subclass__()
        cls.can_focus = can_focus

    @property
    def app(self) -> "App":
        return active_app.get()

    @property
    def console(self) -> Console:
        return active_app.get().console

    @property
    def has_focus(self) -> bool:
        return self._has_focus

    @property
    def mouse_over(self) -> bool:
        return self._mouse_over

    async def refresh(self) -> None:
        self.app.refresh()

    def __rich_repr__(self) -> RichReprResult:
        yield "name", self.name

    def render(
        self, console: Console, options: ConsoleOptions, new_size: WidgetDimensions
    ) -> RenderableType:
        return Panel(
            Align.center(Pretty(self), vertical="middle"),
            title=self.__class__.__name__,
            border_style="green" if self.mouse_over else "blue",
            box=box.HEAVY if self.has_focus else box.ROUNDED,
        )

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        new_size = WidgetDimensions(options.max_width, options.height or console.height)
        renderable = self.render(console, options, new_size)
        self.size = new_size
        yield renderable

    async def post_message(
        self, message: Message, priority: Optional[int] = None
    ) -> bool:
        if not self.check_message_enabled(message):
            return True
        log.debug("%r -> %s", message, self.name)
        return await super().post_message(message, priority)

    async def on_event(self, event: events.Event, priority: int) -> None:
        if isinstance(event, (events.MouseEnter, events.MouseLeave)):
            self._mouse_over = isinstance(event, events.MouseEnter)
            await self.refresh()
        await super().on_event(event, priority)

    async def on_focus(self, event: events.Focus) -> None:
        self._has_focus = True
        await self.refresh()

    async def on_blur(self, event: events.Focus) -> None:
        self._has_focus = False
        await self.refresh()
