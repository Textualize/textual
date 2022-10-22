from __future__ import annotations

from rich import box
from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.pretty import Pretty
import rich.repr
from rich.style import Style

from .. import events
from ..reactive import Reactive
from ..widget import Widget


@rich.repr.auto(angular=False)
class Placeholder(Widget, can_focus=True):

    has_focus: Reactive[bool] = Reactive(False)
    mouse_over: Reactive[bool] = Reactive(False)

    def __init__(
        # parent class constructor signature:
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        # ...and now for our own class specific params:
        title: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.title = title

    def __rich_repr__(self) -> rich.repr.Result:
        yield from super().__rich_repr__()
        yield "has_focus", self.has_focus, False
        yield "mouse_over", self.mouse_over, False

    def render(self) -> RenderableType:
        # Apply colours only inside render_styled
        # Pass the full RICH style object into `render` - not the `Styles`
        return Panel(
            Align.center(
                Pretty(self, no_wrap=True, overflow="ellipsis"),
                vertical="middle",
            ),
            title=self.title or self.__class__.__name__,
            border_style="green" if self.mouse_over else "blue",
            box=box.HEAVY if self.has_focus else box.ROUNDED,
        )

    async def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True

    async def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False

    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False
