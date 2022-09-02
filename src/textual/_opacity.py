from typing import Iterable

from rich.segment import Segment
from rich.style import Style

from textual.color import Color


def _apply_opacity(
    segments: Iterable[Segment],
    base_background: Color,
    opacity: float,
) -> Iterable[Segment]:
    """Takes an iterable of foreground Segments and blends them into the supplied
    background color, yielding copies of the Segments with blended foreground and
    background colors applied.

    Args:
        segments (Iterable[Segment]): The segments in the foreground.
        base_background (Color): The background color to blend foreground into.
        opacity (float): The blending factor. A value of 1.0 means output segments will
            have identical foreground and background colors to input segments.
    """
    _Segment = Segment
    from_rich_color = Color.from_rich_color
    from_color = Style.from_color
    blend = base_background.blend
    for segment in segments:
        text, style, _ = segment
        if not style:
            yield segment
            continue

        blended_style = style
        if style.color:
            color = from_rich_color(style.color)
            blended_foreground = blend(color, factor=opacity)
            blended_style += from_color(color=blended_foreground.rich_color)

        if style.bgcolor:
            bgcolor = from_rich_color(style.bgcolor)
            blended_background = blend(bgcolor, factor=opacity)
            blended_style += from_color(bgcolor=blended_background.rich_color)

        yield _Segment(text, blended_style)
