from rich.markdown import Markdown

from textual import events
from textual.app import App
from textual.view import DockView
from textual.widgets import Header, Footer, Placeholder, ScrollView


class MyApp(App):
    """An example of a very simple Textual App"""

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q,ctrl+c", "quit")
        await self.bind("b", "view.toggle('sidebar')")

    async def on_startup(self, event: events.Startup) -> None:
        view = await self.push_view(DockView())
        header = Header(self.title)
        footer = Footer()
        sidebar = Placeholder(name="sidebar")

        with open("richreadme.md", "rt") as fh:
            readme = Markdown(fh.read(), hyperlinks=True)

        body = ScrollView(readme)

        footer.add_key("b", "Toggle sidebar")
        footer.add_key("q", "Quit")

        await view.dock(header, edge="top")
        await view.dock(footer, edge="bottom")
        await view.dock(sidebar, edge="left", size=30)
        await view.dock(body, edge="right")
        self.require_layout()


app = MyApp(title="Simple App")
app.run()
