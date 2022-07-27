from rich.markdown import Markdown
from rich.syntax import Syntax

from textual.app import App
from textual import events
from textual.widgets import (
    DirectoryTree,
    Tabs,
    Tab,
    ScrollView,
    Header,
    Footer,
)


class TabTest(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")
        await self.bind("1", "switch('0')", "Switch to tab #1")
        await self.bind("2", "switch('1')", "Switch to tab #2")
        await self.bind("3", "switch('2')", "Switch to tab #3")

    async def on_mount(self, event: events.Mount) -> None:
        """Make a simple tab arrangement."""
        await self.view.dock(Header())
        await self.view.dock(Footer(), edge="bottom")

        tab1 = Tab("Rich Readme")
        with open("richreadme.md", "r") as f:
            await tab1.view.dock(ScrollView(Markdown(f.read())))

        tab2 = Tab("Demo Code")
        await tab2.view.dock(ScrollView(Syntax.from_path(__file__)))

        tab3 = Tab("Directory")
        await tab3.view.dock(ScrollView(DirectoryTree("..")))

        self.tabs = Tabs([tab1, tab2, tab3])
        await self.view.dock(self.tabs)

    async def action_switch(self, tab_idx: str) -> None:
        self.tabs.current = int(tab_idx)


TabTest.run(title="Tab Test", log="textual.log")
