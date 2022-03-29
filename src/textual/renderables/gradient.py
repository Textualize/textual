from __future__ import annotations

from rich.console import ConsoleOptions, Console, RenderResult
from rich.color import Color
from rich.segment import Segment
from rich.style import Style

from ._blend_colors import blend_colors_rgb


class VerticalGradient:
    """Draw a vertical gradient."""

    def __init__(self, color1: str, color2: str) -> None:
        self._color1 = Color.parse(color1).get_truecolor()
        self._color2 = Color.parse(color2).get_truecolor()

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width
        height = options.height or options.max_height
        color1 = self._color1
        color2 = self._color2
        default_color = Color.default()
        from_color = Style.from_color
        for y in range(height):
            yield Segment(
                f"{width * ' '}\n",
                from_color(
                    default_color, blend_colors_rgb(color1, color2, y / (height - 1))
                ),
            )


if __name__ == "__main__":
    from rich import print

    print(VerticalGradient("red", "blue"))
