from textual import events
from textual.app import App
from textual.views import DockView
from textual.widgets import Header, Help, Footer, Placeholder, MarkdownViewer


class MyApp(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q, ctrl+c", "quit")
        await self.bind("b", "view.toggle('sidebar')", "Toggle Sidebar")
        await self.bind("h", "view.help")

    async def on_startup(self, event: events.Startup) -> None:
        view = await self.push_view(DockView())
        await view.dock(Header(), edge="top")
        await view.dock(Footer("q", "b", "h"), edge="bottom")
        await view.dock(Placeholder(), edge="left")
        await view.dock(MarkdownViewer("readme.md"))

    async def action_help(self) -> None:
        await self.push_view(Help())


app = MyApp(title="Simple Textual App")
app.run()
