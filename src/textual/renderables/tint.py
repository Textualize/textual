from __future__ import annotations


from rich.console import ConsoleOptions, Console, RenderResult, RenderableType
from rich.segment import Segment
from rich.style import Style

from ..color import Color


class Tint:
    """Applies a color on top of an existing renderable."""

    def __init__(self, renderable: RenderableType, color: Color) -> None:
        """_summary_

        Args:
            renderable (RenderableType): A renderable.
            color (Color): A color (presumably with alpha).
        """
        self.renderable = renderable
        self.color = color

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        segments = console.render(self.renderable, options)

        color = self.color
        from_rich_color = Color.from_rich_color
        style_from_color = Style.from_color
        for segment in segments:
            text, style, control = segment
            if control or style is None:
                yield segment
            else:
                yield Segment(
                    text,
                    (
                        style
                        + style_from_color(
                            (from_rich_color(style.color) + color).rich_color,
                            (from_rich_color(style.bgcolor) + color).rich_color,
                        )
                    ),
                    control,
                )
