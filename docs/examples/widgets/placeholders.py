from textual.app import App
from textual.widgets import Placeholder


class SimpleApp(App):
    """Demonstrates smooth animation"""

    async def on_mount(self) -> None:
        """Build layout here."""

        await self.screen.dock(Placeholder(), edge="left", size=40)
        await self.screen.dock(Placeholder(), Placeholder(), edge="top")


SimpleApp.run(log="textual.log")
