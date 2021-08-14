from rich.panel import Panel

from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget


class Hover(Widget):

    mouse_over = Reactive(False)

    def render(self) -> Panel:
        return Panel("Hello [b]World[/b]", style=("on red" if self.mouse_over else ""))

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False


class HoverApp(App):
    """Demonstrates smooth animation"""

    async def on_mount(self) -> None:
        """Build layout here."""

        hovers = (Hover() for _ in range(10))
        await self.view.dock(*hovers, edge="top")


HoverApp.run(log="textual.log")
