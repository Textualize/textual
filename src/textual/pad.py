from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.measure import Measurement
from rich.segment import Segment


class HorizontalPad:
    """Rich renderable to add padding on the left and right of a renderable."""

    def __init__(self, renderable: RenderableType, left: int, right: int) -> None:
        """
        Initialize HorizontalPad.

        Args:
            renderable: A Rich renderable.
            left: Left padding.
            right: Right padding.
        """
        self.renderable = renderable
        self.left = left
        self.right = right

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        lines = console.render_lines(self.renderable, pad=False)
        new_line = Segment.line()
        left_pad = Segment(" " * self.left)
        right_pad = Segment(" " * self.right)
        for line in lines:
            if self.left:
                yield left_pad
            yield from line
            if self.right:
                yield right_pad
            yield new_line

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        measurement = Measurement.get(console, options, self.renderable)
        total_padding = self.left + self.right
        return Measurement(
            measurement.minimum + total_padding,
            measurement.maximum + total_padding,
        )
