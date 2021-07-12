from rich import box
from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.pretty import Pretty
import rich.repr

from logging import getLogger

from .. import events
from ..widget import Reactive, Widget

log = getLogger("rich")


@rich.repr.auto(angular=False)
class Placeholder(Widget, can_focus=True):

    has_focus: Reactive[bool] = Reactive(False)
    mouse_over: Reactive[bool] = Reactive(False)
    style: Reactive[str] = Reactive("")

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "name", self.name
        yield "has_focus", self.has_focus, False
        yield "mouse_over", self.mouse_over, False

    def render(self) -> RenderableType:
        return Panel(
            Align.center(
                Pretty(self, no_wrap=True, overflow="ellipsis"), vertical="middle"
            ),
            title=self.__class__.__name__,
            border_style="green" if self.mouse_over else "blue",
            box=box.HEAVY if self.has_focus else box.ROUNDED,
            style=self.style,
        )

    async def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True

    async def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False

    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False
