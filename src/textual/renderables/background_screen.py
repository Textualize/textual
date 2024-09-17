from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment
from rich.style import Style

from textual.color import Color

if TYPE_CHECKING:
    from textual.screen import Screen


class BackgroundScreen:
    """Tints a renderable and removes links / meta."""

    def __init__(
        self,
        screen: Screen,
        color: Color,
    ) -> None:
        """Initialize a BackgroundScreen instance.

        Args:
            screen: A Screen instance.
            color: A color (presumably with alpha).
        """
        self.screen = screen
        """Screen to process."""
        self.color = color
        """Color to apply (should have alpha)."""

    @classmethod
    def process_segments(
        cls, segments: Iterable[Segment], color: Color
    ) -> Iterable[Segment]:
        """Apply tint to segments and remove meta + styles

        Args:
            segments: Incoming segments.
            color: Color of tint.

        Returns:
            Segments with applied tint.
        """
        from_rich_color = Color.from_rich_color
        style_from_color = Style.from_color
        _Segment = Segment

        NULL_STYLE = Style()

        if color.a == 0:
            # Special case for transparent color
            for segment in segments:
                text, style, control = segment
                if control:
                    yield segment
                else:
                    yield _Segment(
                        text,
                        NULL_STYLE if style is None else style.clear_meta_and_links(),
                        control,
                    )
            return

        for segment in segments:
            text, style, control = segment
            if control:
                yield segment
            else:
                style = NULL_STYLE if style is None else style.clear_meta_and_links()
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
        segments = console.render(self.screen._compositor, options)
        color = self.color
        return self.process_segments(segments, color)
