import os
import sys

from rich.syntax import Syntax
from rich.text import Text

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
        try:
            syntax = Syntax.from_path(
                message.path,
                line_numbers=True,
                word_wrap=True,
                indent_guides=True,
                theme="monokai",
            )
            self.app.sub_title = os.path.basename(message.path)
            await self.body.update(syntax)

        except Exception as e:
            error_msg = Text().assemble(("\nUh oh... Exception raised!", "bold magenta"), " The file you just clicked is probably not a type that's suited for text-based preview. Try a different file!\n\nException:  ")
            error_msg.append(str(e), style="white on red")
            await self.body.update(error_msg)

        self.body.home()


MyApp.run(title="Code Viewer", log="textual.log")
