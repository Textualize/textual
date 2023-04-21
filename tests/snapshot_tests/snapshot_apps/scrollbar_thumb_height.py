from rich.segment import Segment

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.scroll_view import ScrollView
from textual.strip import Strip
from textual.geometry import Size


class TestScrollView(ScrollView, can_focus=True):
    def __init__(self, height: int, border_title: str) -> None:
        super().__init__()
        self.virtual_size = Size(0, height)
        self.border_title = border_title

    def render_line(self, y: int) -> Strip:
        return Strip(
            [
                Segment(f"Welcome to line {self.scroll_offset.y + y}"),
            ]
        )


class ScrollViewTester(App[None]):
    """Check the scrollbar fits the end."""

    CSS = """
    TestScrollView {
        background: $primary-darken-2;
        border: round red;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield TestScrollView(height=1000, border_title=f"1")
        yield Footer()

    def on_ready(self) -> None:
        self.query_one(TestScrollView).scroll_end(animate=False)


if __name__ == "__main__":
    ScrollViewTester().run()
