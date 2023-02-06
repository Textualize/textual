from rich.segment import Segment

from textual.app import App, ComposeResult
from textual.strip import Strip
from textual.widget import Widget


class CheckerBoard(Widget):
    """Render an 8x8 checkerboard."""

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

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""

        row_index = y // 4  # four lines per row

        if row_index >= 8:
            return Strip.blank(self.size.width)

        is_odd = row_index % 2

        white = self.get_component_rich_style("checkerboard--white-square")
        black = self.get_component_rich_style("checkerboard--black-square")

        segments = [
            Segment(" " * 8, black if (column + is_odd) % 2 else white)
            for column in range(8)
        ]
        strip = Strip(segments, 8 * 8)
        return strip


class BoardApp(App):
    """A simple app to show our widget."""

    def compose(self) -> ComposeResult:
        yield CheckerBoard()


if __name__ == "__main__":
    app = BoardApp()
    app.run()
