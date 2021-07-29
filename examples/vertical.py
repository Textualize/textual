from textual import events
from textual.app import App

from textual.views import WindowView
from textual.widgets import Placeholder


class MyApp(App):
    async def on_mount(self, event: events.Mount) -> None:
        window1 = WindowView(Placeholder(height=20))
        # window2 = WindowView(Placeholder(height=20))

        # window1.scroll_x = -10
        # window1.scroll_y = 5

        await self.view.dock(window1, edge="left")


MyApp.run(log="textual.log")
