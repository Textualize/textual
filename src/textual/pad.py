from typing import cast

from rich.align import Align, AlignMethod
from rich.console import (
    Console,
    ConsoleOptions,
    JustifyMethod,
    RenderableType,
    RenderResult,
)
from rich.measure import Measurement
from rich.segment import Segment, Segments
from rich.style import Style


class HorizontalPad:
    """Rich renderable to add padding on the left and right of a renderable.

    Note that unlike Rich's Padding class this align each line independently.

    """

    def __init__(
        self,
        renderable: RenderableType,
        left: int,
        right: int,
        pad_style: Style,
        justify: JustifyMethod,
    ) -> None:
        """
        Initialize HorizontalPad.

        Args:
            renderable: A Rich renderable.
            left: Left padding.
            right: Right padding.
            pad_style: Style of padding.
            justify: Justify method.
        """
        self.renderable = renderable
        self.left = left
        self.right = right
        self.pad_style = pad_style
        self.justify = justify

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        options = options.update(
            width=options.max_width - self.left - self.right, height=None
        )
        lines = console.render_lines(self.renderable, options, pad=False)
        left_pad = Segment(" " * self.left, self.pad_style)
        right_pad = Segment(" " * self.right, self.pad_style)

        align: AlignMethod = cast(
            AlignMethod,
            self.justify if self.justify in {"left", "right", "center"} else "left",
        )

        for line in lines:
            pad_line = line
            if self.left:
                pad_line = [left_pad, *line]
            if self.right:
                pad_line.append(right_pad)
            segments = Segments(pad_line)
            yield Align(segments, align=align)

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        measurement = Measurement.get(console, options, self.renderable)
        total_padding = self.left + self.right
        return Measurement(
            measurement.minimum + total_padding,
            measurement.maximum + total_padding,
        )
