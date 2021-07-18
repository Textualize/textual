from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Footer, Placeholder


class SmoothApp(App):
    """Demonstrates smooth animation"""

    async def on_load(self, event: events.Load) -> None:
        """Bing keys here."""
        await self.bind("b", "toggle_sidebar", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")

    show_bar: Reactive[bool] = Reactive(False)

    async def watch_show_bar(self, show_bar: bool) -> None:
        """Called when show_bar changes."""
        self.animator.animate(self.bar, "layout_offset_x", 0 if show_bar else -40)

    async def action_toggle_sidebar(self) -> None:
        """Called when user hits b key."""
        self.show_bar = not self.show_bar

    async def on_startup(self, event: events.Startup) -> None:
        """Build layout here."""
        footer = Footer()
        self.bar = Placeholder(name="left")
        self.bar.layout_offset_x = -40

        await self.view.dock(footer, edge="bottom")
        await self.view.dock(self.bar, edge="left", size=40, z=1)
        await self.view.dock(Placeholder(), Placeholder(), edge="top")


SmoothApp.run()
