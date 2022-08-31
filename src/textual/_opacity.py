from typing import Iterable

from rich.segment import Segment
from rich.style import Style

from textual.color import Color
from textual.renderables._blend_colors import blend_colors


def _apply_widget_opacity(
    segments: Iterable[Segment],
    base_background: Color,
    opacity: float,
) -> Iterable[Segment]:
    _Segment = Segment
    for segment in segments:
        text, style, _ = segment
        if not style:
            yield segment
            continue

        color = style.color
        bgcolor = style.bgcolor
        if color and color.triplet and bgcolor and bgcolor.triplet:
            blended_foreground = blend_colors(color, base_background, ratio=opacity)
            blended_background = blend_colors(bgcolor, base_background, ratio=opacity)
            blended_style = Style(color=blended_foreground, bgcolor=blended_background)
            yield _Segment(text, style + blended_style)
        else:
            yield segment
