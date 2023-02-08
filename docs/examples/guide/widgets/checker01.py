from rich.segment import Segment
from rich.style import Style

from textual.app import App, ComposeResult
from textual.strip import Strip
from textual.widget import Widget


class CheckerBoard(Widget):
    """Render an 8x8 checkerboard."""

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""

        row_index = y // 4  # A checkerboard square consists of 4 rows

        if row_index >= 8:  # Generate blank lines when we reach the end
            return Strip.blank(self.size.width)

        is_odd = row_index % 2  # Used to alternate the starting square on each row

        white = Style.parse("on white")  # Get a style object for a white background
        black = Style.parse("on black")  # Get a style object for a black background

        # Generate a list of segments with alternating black and white space characters
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
