from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

from rich.color import Color as RichColor
from rich.segment import Segment
from rich.style import Style

from .color import Color


class LineFilter(ABC):
    """Base class for a line filter."""

    @abstractmethod
    def apply(self, segments: list[Segment]) -> list[Segment]:
        """Transform a list of segments."""


class Monochrome(LineFilter):
    """Convert all colors to monochrome."""

    def apply(self, segments: list[Segment]) -> list[Segment]:
        to_monochrome = self.to_monochrome
        _Segment = Segment
        return [
            _Segment(text, to_monochrome(style), None) for text, style, _ in segments
        ]

    @lru_cache(1024)
    def to_monochrome(self, style: Style) -> Style:
        """Convert colors in a style to monochrome.

        Args:
            style: A Rich Style.

        Returns:
            A new Rich style.
        """
        style_color = style.color
        style_background = style.bgcolor
        color = (
            None
            if style_color is None
            else Color.from_rich_color(style_color).monochrome.rich_color
        )
        background = (
            None
            if style_background is None
            else Color.from_rich_color(style_background).monochrome.rich_color
        )
        return style + Style.from_color(color, background)


NO_DIM = Style(dim=False)
"""A Style to set dim to False."""


# Can be used as a workaround for https://github.com/xtermjs/xterm.js/issues/4161
class DimFilter(LineFilter):
    """Replace dim attributes with modified colors."""

    def __init__(self, dim_factor: float = 0.5) -> None:
        """Initialize the filter.

        Args:
            dim_factor: The factor to dim by; 0 is 100% background (i.e. invisible), 1.0 is no change.
        """
        self.dim_factor = dim_factor

    @lru_cache(1024)
    def dim_color(self, background: RichColor, color: RichColor) -> RichColor:
        """Dim a color by blending towards the background."""
        return (
            Color.from_rich_color(background)
            .blend(Color.from_rich_color(color), self.dim_factor)
            .rich_color
        )

    @lru_cache(1024)
    def dim_style(self, style: Style) -> Style:
        """Replace dim attribute with a dim color"""
        return (
            style
            + Style.from_color(color=self.dim_color(style.bgcolor, style.color))
            + NO_DIM
        )

    def apply(self, segments: list[Segment]) -> list[Segment]:
        """Modify color of segments with dim style."""
        _Segment = Segment
        dim_style = self.dim_style

        return [
            (
                _Segment(
                    segment.text,
                    dim_style(segment.style),
                    None,
                )
                if segment.style is not None and segment.style.dim
                else segment
            )
            for segment in segments
        ]


if __name__ == "__main__":
    from rich.segment import Segments
    from rich.text import Text

    text = Text.from_markup("[dim #ffffff on #0000ff]Hello World!")

    from rich.console import Console

    console = Console()

    segments = list(text.render(console))
    console.print(Segments(segments))
    console.print()
    filter = DimFilter().apply
    console.print(Segments(filter(segments)))
