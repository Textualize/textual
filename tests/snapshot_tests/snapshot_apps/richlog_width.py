from textual.app import App, ComposeResult
from textual.events import Resize
from textual.widgets import RichLog

from rich.text import Text


class RichLogWidth(App[None]):
    def compose(self) -> ComposeResult:
        rich_log = RichLog(min_width=20)
        rich_log.display = False
        rich_log.write(
            Text("written in compose", style="black on white", justify="right"),
            expand=True,
        )
        yield rich_log

    def key_p(self, event: Resize) -> None:
        rich_log: RichLog = self.query_one(RichLog)
        rich_log.display = True
        rich_log.write(Text("hello1", style="on red", justify="right"), expand=True)
        rich_log.visible = False
        rich_log.write(Text("world2", style="on green", justify="right"), expand=True)
        rich_log.visible = True
        rich_log.write(Text("hello3", style="on blue", justify="right"), expand=True)
        rich_log.display = False
        rich_log.write(Text("world4", style="on yellow", justify="right"), expand=True)
        rich_log.display = True


app = RichLogWidth()
if __name__ == "__main__":
    app.run()
