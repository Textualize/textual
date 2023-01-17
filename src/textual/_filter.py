from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

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
