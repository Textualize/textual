from __future__ import annotations

from functools import lru_cache
from math import cos, pi, sin

from rich.color import Color as RichColor
from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment
from rich.style import Style

from ..color import Color, Gradient


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


class LinearGradient:
    """Render a linear gradient with a rotation."""

    def __init__(self, angle: float, stops: list[tuple[float, Color]]) -> None:
        """

        Args:
            angle: Angle of rotation in degrees.
            stops: List of stop consisting of pairs of offset (between 0 and 1) and colors.
        """
        self.angle = angle
        self._stops = stops[:]

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width
        height = options.height or options.max_height

        angle_radians = -self.angle * pi / 180.0
        sin_angle = sin(angle_radians)
        cos_angle = cos(angle_radians)

        center_x = width / 2
        center_y = height

        new_line = Segment.line()

        color_gradient = Gradient(*self._stops)

        _Segment = Segment
        get_color = color_gradient.get_color
        from_color = Style.from_color

        @lru_cache
        def get_rich_color(color_offset: int) -> RichColor:
            """Get a Rich color in the gradient.

            Args:
                color_index: A offset within the color gradient normalized between 0 and 255.

            Returns:
                A Rich color.
            """
            return get_color(color_offset / 255).rich_color

        for line_y in range(height):
            y = float(line_y) * 2
            for x in range(width):
                point_x = x - center_x
                point_y = y - center_y
                rx1 = center_x + (point_x * cos_angle - point_y * sin_angle)
                rx2 = center_x + (point_x * cos_angle - (point_y + 1.0) * sin_angle)
                yield _Segment(
                    "▀",
                    from_color(
                        get_rich_color(int(rx1 / width * 255)),
                        get_rich_color(int(rx2 / width * 255)),
                    ),
                )

            yield new_line


if __name__ == "__main__":
    from rich import print

    COLORS = [
        "#881177",
        "#aa3355",
        "#cc6666",
        "#ee9944",
        "#eedd00",
        "#99dd55",
        "#44dd88",
        "#22ccbb",
        "#00bbcc",
        "#0099cc",
        "#3366bb",
        "#663399",
    ]

    stops = [(i / (len(COLORS) - 1), Color.parse(c)) for i, c in enumerate(COLORS)]

    print(LinearGradient(45, stops))
