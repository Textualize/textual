from __future__ import annotations

from rich.console import ConsoleOptions, Console, RenderResult

from rich.segment import Segment
from rich.style import Style

from ..color import Color


class VerticalGradient:
    """Draw a vertical gradient."""

    def __init__(self, color1: str, color2: str) -> None:
        self._color1 = Color.parse(color1)
        self._color2 = Color.parse(color2)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width
        height = options.height or options.max_height
        color1 = self._color1
        color2 = self._color2
        default_color = Color(0, 0, 0).rich_color
        from_color = Style.from_color
        blend = color1.blend
        rich_color1 = color1.rich_color
        for y in range(height):
            line_color = from_color(
                default_color,
                (
                    blend(color2, y / (height - 1)).rich_color
                    if height > 1
                    else rich_color1
                ),
            )
            yield Segment(f"{width * ' '}\n", line_color)
