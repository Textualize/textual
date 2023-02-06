from __future__ import annotations

from textual.app import App, ComposeResult
from textual.geometry import Size
from textual.strip import Strip
from textual.scroll_view import ScrollView

from rich.segment import Segment


class CheckerBoard(ScrollView):
    COMPONENT_CLASSES = {
        "checkerboard--white-square",
        "checkerboard--black-square",
    }

    DEFAULT_CSS = """
    CheckerBoard .checkerboard--white-square {
        background: #A5BAC9;
    }
    CheckerBoard .checkerboard--black-square {
        background: #004578;
    }
    """

    def __init__(self, board_size: int) -> None:
        super().__init__()
        self.board_size = board_size
        # Each square is 4 rows and 8 columns
        self.virtual_size = Size(board_size * 8, board_size * 4)

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""

        scroll_x, scroll_y = self.scroll_offset  # The current scroll position
        y += scroll_y  # The line at the top of the widget is now `scroll_y`, not zero!
        row_index = y // 4  # four lines per row

        white = self.get_component_rich_style("checkerboard--white-square")
        black = self.get_component_rich_style("checkerboard--black-square")

        if row_index >= self.board_size:
            return Strip.blank(self.size.width)

        is_odd = row_index % 2

        segments = [
            Segment(" " * 8, black if (column + is_odd) % 2 else white)
            for column in range(self.board_size)
        ]
        strip = Strip(segments, self.board_size * 8)
        # Crop the strip so that is covers the visible area
        strip = strip.crop(scroll_x, scroll_x + self.size.width)
        return strip


class BoardApp(App):
    def compose(self) -> ComposeResult:
        yield CheckerBoard(100)


if __name__ == "__main__":
    app = BoardApp()
    app.run()
