import os
import sys

from rich.syntax import Syntax

from textual import events
from textual.app import App
from textual.widgets import Header, Footer, FileClick, ScrollView, DirectoryTree


class MyApp(App):
    """An example of a very simple Textual App"""

    async def on_load(self, event: events.Load) -> None:
        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")

        try:
            self.path = sys.argv[1]
        except IndexError:
            self.path = os.path.abspath(
                os.path.join(os.path.basename(__file__), "../../")
            )

    async def on_mount(self, event: events.Mount) -> None:

        self.body = ScrollView()
        self.directory = DirectoryTree(self.path, "Code")

        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(self.directory, edge="left", size=32, name="sidebar")
        await self.view.dock(self.body, edge="right")

    async def message_file_click(self, message: FileClick) -> None:
        syntax = Syntax.from_path(
            message.path,
            line_numbers=True,
            word_wrap=True,
            indent_guides=True,
            theme="monokai",
        )
        self.app.sub_title = os.path.basename(message.path)
        await self.body.update(syntax)
        self.body.home()


MyApp.run(title="Code Viewer", log="textual.log")
