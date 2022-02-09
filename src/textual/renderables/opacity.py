import functools
from time import sleep

from rich.color import Color
from rich.console import ConsoleOptions, Console, RenderResult, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.segment import Segment
from rich.style import Style
from rich.text import Text

from textual.renderables.utilities import blend_colors


class Opacity:
    """Wrap a renderable to blend foreground color into the background color.

    Args:
        renderable (RenderableType): The RenderableType to manipulate.
        value (float): The opacity as a float. A value of 1.0 means text is fully visible.
    """

    def __init__(self, renderable: RenderableType, value: float = 1.0) -> None:
        self.renderable = renderable
        self.value = value

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        lines = console.render_lines(self.renderable, options)
        opacity = self.value
        for line in lines:
            for segment in line:
                style = segment.style
                if not style:
                    yield segment
                    continue
                fg, bg = style.color, style.bgcolor
                if fg and fg.triplet and bg and bg.triplet:
                    yield Segment(
                        text=segment.text,
                        style=_get_blended_style_cached(
                            fg_color=fg, bg_color=bg, opacity=opacity
                        ),
                        control=segment.control,
                    )
                else:
                    yield segment
            yield ""


@functools.lru_cache(maxsize=1024)
def _get_blended_style_cached(
    fg_color: Color, bg_color: Color, opacity: float
) -> Style:
    return Style.from_color(
        color=blend_colors(bg_color, fg_color, ratio=opacity),
        bgcolor=bg_color,
    )


if __name__ == "__main__":
    console = Console()

    panel = Panel.fit(
        Text("Steak: £30", style="#fcffde on #03761e"),
        title="Menu",
        style="#ffffff on #000000",
    )
    console.print(panel)

    opacity_panel = Opacity(panel, value=0.5)
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
