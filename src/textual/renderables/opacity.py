import functools

from rich.color import Color
from rich.console import ConsoleOptions, Console, RenderResult, RenderableType
from rich.segment import Segment
from rich.style import Style

from textual.renderables._blend_colors import blend_colors


class Opacity:
    """Wrap a renderable to blend foreground color into the background color.

    Args:
        renderable (RenderableType): The RenderableType to manipulate.
        opacity (float): The opacity as a float. A value of 1.0 means text is fully visible.
    """

    def __init__(self, renderable: RenderableType, opacity: float = 1.0) -> None:
        self.renderable = renderable
        self.opacity = opacity

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        segments = console.render(self.renderable, options)
        opacity = self.opacity
        for segment in segments:
            style = segment.style
            if not style:
                yield segment
                continue
            fg = style.color
            bg = style.bgcolor
            if fg and fg.triplet and bg and bg.triplet:
                yield Segment(
                    segment.text,
                    _get_blended_style_cached(
                        fg_color=fg, bg_color=bg, opacity=opacity
                    ),
                    segment.control,
                )
            else:
                yield segment


@functools.lru_cache(maxsize=1024)
def _get_blended_style_cached(
    fg_color: Color, bg_color: Color, opacity: float
) -> Style:
    return Style.from_color(
        color=blend_colors(bg_color, fg_color, ratio=opacity),
        bgcolor=bg_color,
    )


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

    opacity_panel = Opacity(panel, opacity=0.5)
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
