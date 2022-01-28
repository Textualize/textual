from __future__ import annotations

import random

from rich.color import Color, ANSI_COLOR_NAMES
from rich.console import ConsoleOptions, Console, RenderResult
from rich.segment import Segment
from rich.style import Style


class UnderlineBar:
    def __init__(
        self,
        highlight_range: tuple[float, float] = 0,
        range_color: Color = Color.parse("yellow"),
        other_color: Color = Color.parse("default"),
        background_color: Color = Color.parse("default"),
        width: int | None = None,
    ) -> None:
        self.highlight_range = highlight_range
        self.highlight_style = Style.from_color(
            color=range_color, bgcolor=background_color
        )
        self.other_style = Style.from_color(color=other_color, bgcolor=background_color)
        self.width = width

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        half_bar_right = "╸"
        half_bar_left = "╺"
        bar = "━"
        width = (self.width or options.max_width) - 1
        start, end = self.highlight_range

        # Round start and end to nearest half
        start = round(start * 2) / 2
        end = round(end * 2) / 2

        half_start = start - int(start) > 0
        half_end = end - int(end) > 0

        # Initial non-highlighted portion of bar
        yield Segment(bar * (int(start - 0.5)), style=self.other_style)
        if not half_start and start > 0:
            yield Segment(half_bar_right, style=self.other_style)

        # If we have a half bar at start and end, we need 1 less full bar
        full_bar_width = int(end) - int(start)
        if half_start and half_end:
            full_bar_width -= 1

        # The highlighted portion
        if not half_start:
            yield Segment(bar * full_bar_width, style=self.highlight_style)
        else:
            yield Segment(half_bar_left, style=self.highlight_style)
            yield Segment(bar * full_bar_width, style=self.highlight_style)
        if half_end:
            yield Segment(half_bar_right, style=self.highlight_style)

        # The non-highlighted tail
        if not half_end and end - width != 1:
            yield Segment(half_bar_left, style=self.other_style)
        yield Segment(bar * (int(width) - int(end)), style=self.other_style)


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

    start_range = frange(0, 12, 0.5)
    end_range = frange(6, 18, 0.5)
    ranges = zip(start_range, end_range)

    for range in ranges:
        color = random.choice(list(ANSI_COLOR_NAMES.keys()))
        console.print(
            UnderlineBar(
                range,
                range_color=Color.parse(color),
                other_color=Color.parse("#4f4f4f"),
                width=18,
            )
        )
        console.print()
