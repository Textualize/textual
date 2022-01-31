from __future__ import annotations

import random

from rich.color import Color, ANSI_COLOR_NAMES
from rich.console import ConsoleOptions, Console, RenderResult
from rich.segment import Segment
from rich.style import Style


class UnderlineBar:
    """Thin horizontal bar with a portion highlighted.

    Args:
        highlight_range (tuple[float, float]): The range to highlight. Defaults to ``(0, 0)`` (no highlight)
        highlight_color (Color | str): The color of the highlighted range of the bar.
        non_highlight_color (Color | str): The color of the non-highlighted range(s) of the bar.
        background_color (Color | str): The background color of the entire bar.
        width (int, optional): The width of the bar, or ``None`` to fill available width.
    """

    def __init__(
        self,
        highlight_range: tuple[float, float] = (0, 0),
        highlight_color: Color | str = "magenta",
        non_highlight_color: Color | str = "grey37",
        background_color: Color | str = "default",
        width: int | None = None,
    ) -> None:
        self.highlight_range = highlight_range
        self.highlight_style = Style(color=highlight_color, bgcolor=background_color)
        self.non_highlight_style = Style(
            color=non_highlight_color, bgcolor=background_color
        )
        self.width = width

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        half_bar_right = "╸"
        half_bar_left = "╺"
        bar = "━"
        width = self.width or options.max_width
        start, end = self.highlight_range

        start = max(start, 0)
        end = min(end, width)

        if start == end == 0:
            yield Segment(bar * width, style=self.non_highlight_style)
            return

        # Round start and end to nearest half
        start = round(start * 2) / 2
        end = round(end * 2) / 2

        # Check if we start/end on a number that rounds to a .5
        half_start = start - int(start) > 0
        half_end = end - int(end) > 0

        # Initial non-highlighted portion of bar
        yield Segment(bar * (int(start - 0.5)), style=self.non_highlight_style)
        if not half_start and start > 0:
            yield Segment(half_bar_right, style=self.non_highlight_style)

        # The highlighted portion
        bar_width = int(end) - int(start)
        if half_start:
            yield Segment(
                half_bar_left + bar * (bar_width - 1), style=self.highlight_style
            )
        else:
            yield Segment(bar * bar_width, style=self.highlight_style)
        if half_end:
            yield Segment(half_bar_right, style=self.highlight_style)

        # The non-highlighted tail
        if not half_end and end - width != 0:
            yield Segment(half_bar_left, style=self.non_highlight_style)
        yield Segment(bar * (int(width) - int(end) - 1), style=self.non_highlight_style)


if __name__ == "__main__":
    console = Console()

    def frange(start, end, step):
        current = start
        while current < end:
            yield current
            current += step

        while current >= 0:
            yield current
            current -= step

    step = 0.5
    start_range = frange(0.5, 10.5, step)
    end_range = frange(10, 20, step)
    ranges = zip(start_range, end_range)

    console.print(UnderlineBar(width=20), f"   (.0, .0)")

    for range in ranges:
        color = random.choice(list(ANSI_COLOR_NAMES.keys()))
        console.print(
            UnderlineBar(
                range,
                highlight_color=Color.parse(color),
                width=20,
            ),
            f"   {range}",
        )
