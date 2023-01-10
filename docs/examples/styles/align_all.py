from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Label


class AlignAllApp(App):
    """App that illustrates all alignments."""

    CSS_PATH = "align_all.css"

    def compose(self) -> ComposeResult:
        yield Container(Label("left top"), id="left-top")
        yield Container(Label("center top"), id="center-top")
        yield Container(Label("right top"), id="right-top")
        yield Container(Label("left middle"), id="left-middle")
        yield Container(Label("center middle"), id="center-middle")
        yield Container(Label("right middle"), id="right-middle")
        yield Container(Label("left bottom"), id="left-bottom")
        yield Container(Label("center bottom"), id="center-bottom")
        yield Container(Label("right bottom"), id="right-bottom")
