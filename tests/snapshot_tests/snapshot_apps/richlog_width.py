from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import RichLog


class RichLogWidth(App[None]):
    def compose(self) -> ComposeResult:
        yield RichLog(min_width=20)

app = RichLogWidth()
if __name__ == "__main__":
    app.run()
