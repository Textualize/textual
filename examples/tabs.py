from rich.markdown import Markdown
from rich.syntax import Syntax

from textual.app import App
from textual import events
from textual.widgets import DirectoryTree, Tabs, Tab, ScrollView, Header, Footer


class TabTest(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:
        """Make a simple tab arrangement."""
        await self.view.dock(Header())
        await self.view.dock(Footer(), edge="bottom")

        tab1 = Tab("Rich Readme")
        with open("richreadme.md", "r") as f:
            await tab1.view.dock(ScrollView(Markdown(f.read())))

        tab2 = Tab("Demo Code")
        await tab2.view.dock(ScrollView(Syntax.from_path("tabs.py")))

        tab3 = Tab("Directory")
        await tab3.view.dock(ScrollView(DirectoryTree("..")))

        tabs = Tabs([tab1, tab2, tab3])
        await self.view.dock(tabs)


TabTest.run(title="Tab Test", log="textual.log")
