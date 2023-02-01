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
        "checkerboard--void",
    }

    DEFAULT_CSS = """
    CheckerBoard {
        background: $primary;
    }
    CheckerBoard .checkerboard--void {
        background: $background;
    }

    CheckerBoard .checkerboard--white-square {
        background: $foreground 70%;
    }
    CheckerBoard .checkerboard--black-square {
        background: $primary;
    }
    """

    def on_mount(self) -> None:
        self.virtual_size = Size(64, 32)

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""

        scroll_x, scroll_y = self.scroll_offset
        y += scroll_y
        row_index = y // 4  # four lines per row

        white = self.get_component_rich_style("checkerboard--white-square")
        black = self.get_component_rich_style("checkerboard--black-square")
        void = self.get_component_rich_style("checkerboard--void")

        if row_index >= 8:
            return Strip.blank(self.size.width, void)

        is_odd = row_index % 2

        segments = [
            Segment(" " * 8, black if (column + is_odd) % 2 else white)
            for column in range(8)
        ]
        strip = Strip(segments, 8 * 8)
        strip = strip.extend_cell_length(self.size.width, void)
        strip = strip.crop(scroll_x, scroll_x + self.size.width)
        return strip


class BoardApp(App):
    def compose(self) -> ComposeResult:
        yield CheckerBoard()


if __name__ == "__main__":
    app = BoardApp()
    app.run()
