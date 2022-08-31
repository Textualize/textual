from typing import Iterable

from rich.segment import Segment
from rich.style import Style

from textual.color import Color


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

        blended_style = style
        if style.color:
            color = Color.from_rich_color(style.color)
            blended_foreground = base_background.blend(color, factor=opacity)
            blended_style = style + Style.from_color(
                color=blended_foreground.rich_color
            )

        if style.bgcolor:
            bgcolor = Color.from_rich_color(style.bgcolor)
            blended_background = base_background.blend(bgcolor, factor=opacity)
            blended_style = blended_style + Style.from_color(
                bgcolor=blended_background.rich_color
            )

        yield _Segment(text, blended_style)
