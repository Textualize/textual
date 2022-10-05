from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class OffsetExample(App):
    def compose(self) -> ComposeResult:
        yield Vertical(Static("Child", id="child"), id="parent")
        yield Static("Tag", id="tag")


app = OffsetExample(css_path="offset.css")
if __name__ == "__main__":
    app.run()
