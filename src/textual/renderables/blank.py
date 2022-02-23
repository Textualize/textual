from __future__ import annotations

from rich.console import ConsoleOptions, Console, RenderResult
from rich.color import Color
from rich.segment import Segment
from rich.style import Style


class Blank:
    """Draw solid background color."""

    def __init__(self, color: str) -> None:
        self._style = Style.from_color(None, Color.parse(color))

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width
        height = options.height or options.max_height

        segment = Segment(f"{' ' * width}\n", self._style)
        yield from [segment] * height


if __name__ == "__main__":
    from rich import print

    print(Blank("red"))
