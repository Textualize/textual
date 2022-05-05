from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Footer, Placeholder


class SmoothApp(App):
    """Demonstrates smooth animation. Press 'b' to see it in action."""

    async def on_load(self) -> None:
        """Bind keys here."""
        await self.bind("b", "toggle_sidebar", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")

    show_bar = Reactive(False)

    def watch_show_bar(self, show_bar: bool) -> None:
        """Called when show_bar changes."""
        self.bar.animate("layout_offset_x", 0 if show_bar else -40)

    def action_toggle_sidebar(self) -> None:
        """Called when user hits 'b' key."""
        self.show_bar = not self.show_bar

    async def on_mount(self) -> None:
        """Build layout here."""
        footer = Footer()
        self.bar = Placeholder(name="left")

        await self.screen.dock(footer, edge="bottom")
        await self.screen.dock(Placeholder(), Placeholder(), edge="top")
        await self.screen.dock(self.bar, edge="left", size=40, z=1)

        self.bar.layout_offset_x = -40

        # self.set_timer(10, lambda: self.action("quit"))


SmoothApp.run(log_path="textual.log", log_verbosity=2)
