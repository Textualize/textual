from __future__ import annotations

from typing import Iterable

from rich.console import RenderableType
from rich.segment import Segment
from rich.style import Style
from rich.terminal_theme import TerminalTheme

from textual.color import Color
from textual.filter import ANSIToTruecolor


class Tint:
    """Applies a color on top of an existing renderable."""

    def __init__(
        self,
        renderable: RenderableType,
        color: Color,
    ) -> None:
        """Wrap a renderable to apply a tint color.

        Args:
            renderable: A renderable.
            color: A color (presumably with alpha).
        """
        self.renderable = renderable
        self.color = color

    @classmethod
    def process_segments(
        cls, segments: Iterable[Segment], color: Color, ansi_theme: TerminalTheme
    ) -> Iterable[Segment]:
        """Apply tint to segments.

        Args:
            segments: Incoming segments.
            color: Color of tint.
            ansi_theme: The TerminalTheme defining how to map ansi colors to hex.

        Returns:
            Segments with applied tint.
        """
        from_rich_color = Color.from_rich_color
        style_from_color = Style.from_color
        _Segment = Segment

        truecolor_style = ANSIToTruecolor(ansi_theme).truecolor_style

        NULL_STYLE = Style()
        for segment in segments:
            text, style, control = segment
            if control:
                yield segment
            else:
                style = truecolor_style(style) if style is not None else NULL_STYLE
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
