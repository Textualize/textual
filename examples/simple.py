from rich.markdown import Markdown

from textual import events
from textual.app import App
from textual.widgets.header import Header
from textual.widgets.placeholder import Placeholder
from textual.widgets.window import Window

with open("richreadme.md", "rt") as fh:
    readme = Markdown(fh.read(), hyperlinks=True, code_theme="fruity")


class MyApp(App):

    KEYS = {"q": "quit", "ctrl+c": "quit"}

    async def on_startup(self, event: events.Startup) -> None:
        await self.view.mount_all(
            header=Header(self.title), left=Placeholder(), body=Window(readme)
        )


app = MyApp()
app.run()
