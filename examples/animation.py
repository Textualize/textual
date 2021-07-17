from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.views import DockView
from textual.widgets import Footer, Placeholder


class SmoothApp(App):
    """Demonstrates smooth animation"""

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q,ctrl+c", "quit")
        await self.bind("x", "bang")
        await self.bind("b", "toggle_sidebar")

    show_bar: Reactive[bool] = Reactive(False)

    async def watch_show_bar(self, show_bar: bool) -> None:
        self.animator.animate(self.bar, "layout_offset_x", 0 if show_bar else -40)

    async def action_toggle_sidebar(self) -> None:
        self.show_bar = not self.show_bar

    async def on_startup(self, event: events.Startup) -> None:

        view = await self.push_view(DockView())

        footer = Footer()
        self.bar = Placeholder(name="left")
        self.bar.layout_offset_x = -40

        footer.add_key("b", "Toggle sidebar")
        footer.add_key("q", "Quit")

        await view.dock(footer, edge="bottom")
        await view.dock(self.bar, edge="left", size=40, z=1)

        await view.dock(Placeholder(), Placeholder(), edge="top")


SmoothApp.run()