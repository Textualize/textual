import functools
from typing import Iterable

from rich.cells import cell_len
from rich.color import Color
from rich.console import ConsoleOptions, Console, RenderResult, RenderableType
from rich.segment import Segment
from rich.style import Style

from textual.renderables._blend_colors import blend_colors


@functools.lru_cache(maxsize=1024)
def _get_blended_style_cached(
    bg_color: Color, fg_color: Color, opacity: float
) -> Style:
    """Blend from one color to another.

    Cached because when a UI is static the opacity will be constant.

    Args:
        bg_color (Color): Background color.
        fg_color (Color): Foreground color.
        opacity (float): Opacity.

    Returns:
        Style: Resulting style.
    """
    return Style.from_color(
        color=blend_colors(bg_color, fg_color, ratio=opacity),
        bgcolor=bg_color,
    )


class TextOpacity:
    """Blend foreground in to background."""

    def __init__(self, renderable: RenderableType, opacity: float = 1.0) -> None:
        """Wrap a renderable to blend foreground color into the background color.

        Args:
            renderable (RenderableType): The RenderableType to manipulate.
            opacity (float): The opacity as a float. A value of 1.0 means text is fully visible.
        """
        self.renderable = renderable
        self.opacity = opacity

    @classmethod
    def process_segments(
        cls, segments: Iterable[Segment], opacity: float
    ) -> Iterable[Segment]:
        """Apply opacity to segments.

        Args:
            segments (Iterable[Segment]): Incoming segments.
            opacity (float): Opacity to apply.

        Returns:
            Iterable[Segment]: Segments with applied opacity.

        """
        _Segment = Segment
        _from_color = Style.from_color
        if opacity == 0:
            for text, style, control in segments:
                invisible_style = _from_color(bgcolor=style.bgcolor)
                yield _Segment(cell_len(text) * " ", invisible_style)
        else:
            for segment in segments:
                text, style, control = segment
                if not style:
                    yield segment
                    continue

                color = style.color
                bgcolor = style.bgcolor
                if color and color.triplet and bgcolor and bgcolor.triplet:
                    color_style = _get_blended_style_cached(bgcolor, color, opacity)
                    yield _Segment(text, style + color_style)
                else:
                    yield segment

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        segments = console.render(self.renderable, options)
        return self.process_segments(segments, self.opacity)


if __name__ == "__main__":
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text

    from time import sleep

    console = Console()

    panel = Panel.fit(
        Text("Steak: £30", style="#fcffde on #03761e"),
        title="Menu",
        style="#ffffff on #000000",
    )
    console.print(panel)

    opacity_panel = TextOpacity(panel, opacity=0.5)
    console.print(opacity_panel)

    def frange(start, end, step):
        current = start
        while current < end:
            yield current
            current += step

        while current >= 0:
            yield current
            current -= step

    import itertools

    with Live(opacity_panel, refresh_per_second=60) as live:
        for value in itertools.cycle(frange(0, 1, 0.05)):
            opacity_panel.value = value
            sleep(0.05)
