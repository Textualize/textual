from __future__ import annotations

from textual import events
from textual.app import App, ComposeResult
from textual.geometry import Offset, Region, Size
from textual.reactive import var
from textual.strip import Strip
from textual.scroll_view import ScrollView

from rich.segment import Segment
from rich.style import Style


class CheckerBoard(ScrollView):
    COMPONENT_CLASSES = {
        "checkerboard--white-square",
        "checkerboard--black-square",
        "checkerboard--cursor-square",
    }

    DEFAULT_CSS = """
    CheckerBoard > .checkerboard--white-square {
        background: #A5BAC9;
    }
    CheckerBoard > .checkerboard--black-square {
        background: #004578;
    }
    CheckerBoard > .checkerboard--cursor-square {
        background: darkred;
    }
    """

    cursor_square = var(Offset(0, 0))

    def __init__(self, board_size: int) -> None:
        super().__init__()
        self.board_size = board_size
        # Each square is 4 rows and 8 columns
        self.virtual_size = Size(board_size * 8, board_size * 4)

    def on_mouse_move(self, event: events.MouseMove) -> None:
        """Called when the user moves the mouse over the widget."""
        mouse_position = event.offset + self.scroll_offset
        self.cursor_square = Offset(mouse_position.x // 8, mouse_position.y // 4)

    def watch_cursor_square(
        self, previous_square: Offset, cursor_square: Offset
    ) -> None:
        """Called when the cursor square changes."""

        def get_square_region(square_offset: Offset) -> Region:
            """Get region relative to widget from square coordinate."""
            x, y = square_offset
            region = Region(x * 8, y * 4, 8, 4)
            # Move the region into the widgets frame of reference
            region = region.translate(-self.scroll_offset)
            return region

        # Refresh the previous cursor square
        self.refresh(get_square_region(previous_square))

        # Refresh the new cursor square
        self.refresh(get_square_region(cursor_square))

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""

        scroll_x, scroll_y = self.scroll_offset  # The current scroll position
        y += scroll_y  # The line at the top of the widget is now `scroll_y`, not zero!
        row_index = y // 4  # four lines per row

        white = self.get_component_rich_style("checkerboard--white-square")
        black = self.get_component_rich_style("checkerboard--black-square")
        cursor = self.get_component_rich_style("checkerboard--cursor-square")

        if row_index >= self.board_size:
            return Strip.blank(self.size.width)

        is_odd = row_index % 2

        def get_square_style(column: int, row: int) -> Style:
            """Get the cursor style at the given position on the checkerboard."""
            if self.cursor_square == Offset(column, row):
                square_style = cursor
            else:
                square_style = black if (column + is_odd) % 2 else white
            return square_style

        segments = [
            Segment(" " * 8, get_square_style(column, row_index))
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
