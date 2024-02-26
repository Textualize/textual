"""Filter classes.

!!! note

    Filters are used internally, and not recommended for use by Textual app developers.

Filters are used internally to process terminal output after it has been rendered.
Currently this is used internally to convert the application to monochrome, when the NO_COLOR env var is set.

In the future, this system will be used to implement accessibility features.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

from rich.color import Color as RichColor
from rich.segment import Segment
from rich.style import Style
from rich.terminal_theme import TerminalTheme

from .color import Color


class LineFilter(ABC):
    """Base class for a line filter."""

    @abstractmethod
    def apply(self, segments: list[Segment], background: Color) -> list[Segment]:
        """Transform a list of segments.

        Args:
            segments: A list of segments.
            background: The background color.

        Returns:
            A new list of segments.
        """


@lru_cache(1024)
def monochrome_style(style: Style) -> Style:
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


class Monochrome(LineFilter):
    """Convert all colors to monochrome."""

    def apply(self, segments: list[Segment], background: Color) -> list[Segment]:
        """Transform a list of segments.

        Args:
            segments: A list of segments.
            background: The background color.

        Returns:
            A new list of segments.
        """
        _monochrome_style = monochrome_style
        _Segment = Segment
        return [
            _Segment(text, _monochrome_style(style), None)
            for text, style, _ in segments
        ]


NO_DIM = Style(dim=False)
"""A Style to set dim to False."""


@lru_cache(1024)
def dim_color(background: RichColor, color: RichColor, factor: float) -> RichColor:
    """Dim a color by blending towards the background

    Args:
        background: background color.
        color: Foreground color.
        factor: Blend factor

    Returns:
        New dimmer color.
    """
    red1, green1, blue1 = background.triplet
    red2, green2, blue2 = color.triplet

    return RichColor.from_rgb(
        red1 + (red2 - red1) * factor,
        green1 + (green2 - green1) * factor,
        blue1 + (blue2 - blue1) * factor,
    )


DEFAULT_COLOR = RichColor.default()


@lru_cache(1024)
def dim_style(style: Style, background: Color, factor: float) -> Style:
    """Replace dim attribute with a dim color.

    Args:
        style: Style to dim.
        factor: Blend factor.

    Returns:
        New dimmed style.
    """
    return (
        style
        + Style.from_color(
            dim_color(
                (background.rich_color if style.bgcolor.is_default else style.bgcolor),
                style.color,
                factor,
            ),
            None,
        )
    ) + NO_DIM


# Can be used as a workaround for https://github.com/xtermjs/xterm.js/issues/4161
class DimFilter(LineFilter):
    """Replace dim attributes with modified colors."""

    def __init__(self, dim_factor: float = 0.5) -> None:
        """Initialize the filter.

        Args:
            dim_factor: The factor to dim by; 0 is 100% background (i.e. invisible), 1.0 is no change.
        """
        self.dim_factor = dim_factor

    def apply(self, segments: list[Segment], background: Color) -> list[Segment]:
        """Transform a list of segments.

        Args:
            segments: A list of segments.
            background: The background color.

        Returns:
            A new list of segments.
        """
        _Segment = Segment
        _dim_style = dim_style
        factor = self.dim_factor

        return [
            (
                _Segment(
                    segment.text,
                    _dim_style(segment.style, background, factor),
                    None,
                )
                if segment.style is not None and segment.style.dim
                else segment
            )
            for segment in segments
        ]


class ANSIToTruecolor(LineFilter):
    """Convert ANSI colors to their truecolor equivalents."""

    def __init__(self, terminal_theme: TerminalTheme):
        """Initialise filter.

        Args:
            terminal_theme: A rich terminal theme.
        """
        self._terminal_theme = terminal_theme

    @lru_cache(1024)
    def truecolor_style(self, style: Style) -> Style:
        """Replace system colors with truecolor equivalent.

        Args:
            style: Style to apply truecolor filter to.

        Returns:
            New style.
        """
        terminal_theme = self._terminal_theme
        color = style.color
        if color is not None and color.is_system_defined:
            color = RichColor.from_rgb(
                *color.get_truecolor(terminal_theme, foreground=True)
            )
        bgcolor = style.bgcolor
        if bgcolor is not None and bgcolor.is_system_defined:
            bgcolor = RichColor.from_rgb(
                *bgcolor.get_truecolor(terminal_theme, foreground=False)
            )

        return style + Style.from_color(color, bgcolor)

    def apply(self, segments: list[Segment], background: Color) -> list[Segment]:
        """Transform a list of segments.

        Args:
            segments: A list of segments.
            background: The background color.

        Returns:
            A new list of segments.
        """
        _Segment = Segment
        truecolor_style = self.truecolor_style

        return [
            _Segment(
                text,
                None if style is None else truecolor_style(style),
                None,
            )
            for text, style, _ in segments
        ]
