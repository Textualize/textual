from textual import events
from textual.app import App, Bind
from textual.widgets import Header, Placeholder, MarkdownViewer


class MyApp(App):
    KEYS = {
        "q, ctrl+c": Bind("quit"),
        "b": Bind("view.toggle('left')", "Toggle Sidebar"),
    }

    async def on_load(self, event: events.Load) -> None:
        self.bind(self.KEYS)

    async def on_startup(self, event: events.Startup) -> None:
        await self.view.mount(
            header=Header(),
            left=Placeholder(),
            body=MarkdownViewer("readme.md"),
        )


app = MyApp(title="Simple Textual App")
app.run()
