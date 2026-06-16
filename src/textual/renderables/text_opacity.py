import functools
from typing import Iterable, Tuple, cast

from rich.cells import cell_len
from rich.color import Color
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment
from rich.style import Style
from rich.terminal_theme import TerminalTheme

from textual._ansi_theme import DEFAULT_TERMINAL_THEME
from textual._context import active_app
from textual.color import TRANSPARENT
from textual.filter import ANSIToTruecolor
from textual.renderables._blend_colors import blend_colors


@functools.lru_cache(maxsize=1024)
def _get_blended_style_cached(
    bg_color: Color, fg_color: Color, opacity: float
) -> Style:
    """Blend from one color to another.

    Cached because when a UI is static the opacity will be constant.

    Args:
        bg_color: Background color.
        fg_color: Foreground color.
        opacity: Opacity.

    Returns:
        Resulting style.
    """
    return Style.from_color(
        color=blend_colors(bg_color, fg_color, ratio=opacity),
        bgcolor=bg_color,
    )


class TextOpacity:
    """Blend foreground into background."""

    def __init__(self, renderable: RenderableType, opacity: float = 1.0) -> None:
        """Wrap a renderable to blend foreground color into the background color.

        Args:
            renderable: The RenderableType to manipulate.
            opacity: The opacity as a float. A value of 1.0 means text is fully visible.
        """
        self.renderable = renderable
        self.opacity = opacity

    @classmethod
    def process_segments(
        cls,
        segments: Iterable[Segment],
        opacity: float,
        ansi_theme: TerminalTheme,
        native_ansi: bool = False,
    ) -> Iterable[Segment]:
        """Apply opacity to segments.

        Args:
            segments: Incoming segments.
            opacity: Opacity to apply.
            ansi_theme: Terminal theme.
            background: Color of background.
            native_ansi: Allow ANSI colors.

        Returns:
            Segments with applied opacity.
        """

        _Segment = Segment
        _from_color = Style.from_color
        if opacity == 0:
            for text, style, _control in cast(
                # use Tuple rather than tuple so Python 3.7 doesn't complain
                Iterable[Tuple[str, Style, object]],
                segments,
            ):
                invisible_style = _from_color(bgcolor=style.bgcolor)
                yield _Segment(cell_len(text) * " ", invisible_style)
        elif opacity == 1:
            yield from segments
        else:
            if native_ansi:
                # Special case for native ANSI
                # Without RGB we can't accurately calculate the foreground color
                DIM = Style(dim=True)
                filter = ANSIToTruecolor(ansi_theme)
                segments_ = list(segments)
                for original_segment, segment in zip(
                    segments_, filter.apply(segments_, TRANSPARENT)
                ):
                    if original_segment.style is not None:
                        text, style, control = original_segment
                        if (
                            style is not None
                            and style.bgcolor is not None
                            and style.bgcolor.is_default
                        ):
                            # If the opacity is less than or equal to 50%, then set the dim attribute
                            if style.color is not None and opacity <= 0.5:
                                yield Segment(text, style + DIM, control)
                            else:
                                yield original_segment
                            continue
                    # use Tuple rather than tuple so Python 3.7 doesn't complain
                    text, style, control = segment
                    if not style:
                        yield segment
                        continue

                    color = style.color
                    bgcolor = style.bgcolor
                    if (
                        color is not None
                        and color.triplet
                        and bgcolor
                        and bgcolor.triplet
                    ):
                        color_style = _get_blended_style_cached(bgcolor, color, opacity)
                        yield _Segment(text, style + color_style)
                    else:
                        yield segment
            else:
                filter = ANSIToTruecolor(ansi_theme)
                for segment in filter.apply(list(segments), TRANSPARENT):
                    # use Tuple rather than tuple so Python 3.7 doesn't complain
                    text, style, control = segment
                    if not style:
                        yield segment
                        continue

                    color = style.color
                    bgcolor = style.bgcolor
                    if (
                        color is not None
                        and color.triplet
                        and bgcolor
                        and bgcolor.triplet
                    ):
                        color_style = _get_blended_style_cached(bgcolor, color, opacity)
                        yield _Segment(text, style + color_style)
                    else:
                        yield segment

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        try:
            app = active_app.get()
        except LookupError:
            ansi_theme = DEFAULT_TERMINAL_THEME
        else:
            ansi_theme = app.ansi_theme
        segments = console.render(self.renderable, options)
        return self.process_segments(segments, self.opacity, ansi_theme)
