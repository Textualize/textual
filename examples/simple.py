import logging
from logging import FileHandler

from rich.markdown import Markdown

from textual import events
from textual.app import App
from textual.views import DockView
from textual.widgets import Header, Footer, Placeholder, ScrollView


logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[FileHandler("richtui.log")],
)

log = logging.getLogger("rich")


class MyApp(App):
    """An example of a very simple Textual App"""

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q,ctrl+c", "quit", "Quit")
        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")

    async def on_startup(self, event: events.Startup) -> None:

        view = await self.push_view(DockView())

        footer = Footer()
        footer.add_key("b", "Toggle sidebar")
        footer.add_key("q", "Quit")
        header = Header()
        body = ScrollView()
        sidebar = Placeholder()

        await view.dock(header, edge="top")
        await view.dock(footer, edge="bottom")
        await view.dock(sidebar, edge="left", size=30, name="sidebar")
        await view.dock(body, edge="right")

        async def get_markdown(filename: str) -> None:
            with open(filename, "rt") as fh:
                readme = Markdown(fh.read(), hyperlinks=True)
            await body.update(readme)

        await self.call_later(get_markdown, "richreadme.md")


MyApp.run(title="Simple App")
