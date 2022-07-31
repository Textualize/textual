from __future__ import annotations

from typing import Iterable

from rich.console import ConsoleOptions, Console, RenderResult, RenderableType
from rich.segment import Segment
from rich.style import Style

from ..color import Color


class Tint:
    """Applies a color on top of an existing renderable."""

    def __init__(self, renderable: RenderableType, color: Color) -> None:
        """Wrap a renderable to apply a tint color.

        Args:
            renderable (RenderableType): A renderable.
            color (Color): A color (presumably with alpha).
        """
        self.renderable = renderable
        self.color = color

    @classmethod
    def process_segments(
        cls, segments: Iterable[Segment], color: Color
    ) -> Iterable[Segment]:
        """Apply tint to segments.

        Args:
            segments (Iterable[Segment]): Incoming segments.
            color (Color): Color of tint.

        Returns:
            Iterable[Segment]: Segments with applied tint.

        """
        from_rich_color = Color.from_rich_color
        style_from_color = Style.from_color
        _Segment = Segment

        NULL_STYLE = Style()
        for segment in segments:
            text, style, control = segment
            if control:
                yield segment
            else:
                style = style or NULL_STYLE
                yield _Segment(
                    text,
                    (
                        style
                        + style_from_color(
                            (
                                (from_rich_color(style.color) + color).rich_color
                                if style.color is not None
                                else None
                            ),
                            (
                                (from_rich_color(style.bgcolor) + color).rich_color
                                if style.bgcolor is not None
                                else None
                            ),
                        )
                    ),
                    control,
                )

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        segments = console.render(self.renderable, options)
        color = self.color
        return self.process_segments(segments, color)
