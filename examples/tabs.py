from textual.app import App
from textual import events
from textual.widgets import Placeholder, Tabs, Tab


class TabTest(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:
        """Make a simple tab arrangement."""
        tab1 = Tab("First Tab Label")
        await tab1.view.dock(Placeholder())

        tab2 = Tab("Second Tab Label")
        await tab2.view.dock(Placeholder())

        tabs = Tabs([tab1, tab2])
        await self.view.dock(tabs)


TabTest.run(title="Tab Test", log="textual.log")
