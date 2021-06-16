from __future__ import annotations

from math import ceil
import logging


from rich.color import Color
from rich.style import Style
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.segment import Segment
from rich.style import Style

log = logging.getLogger("rich")


class VerticalBar:
    def __init__(
        self,
        lines: list[list[Segment]],
        height: int,
        virtual_height: int,
        position: float,
        overlay: bool = False,
    ) -> None:
        self.lines = lines
        self.height = height
        self.virtual_height = virtual_height
        self.position = position
        self.overlay = overlay

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        bar = render_bar(
            size=self.height,
            window_size=len(self.lines),
            virtual_size=self.virtual_height,
            position=self.position,
        )
        new_line = Segment.line()
        for line, bar_segment in zip(self.lines, bar):
            yield from line
            yield bar_segment
            yield new_line


def render_bar(
    size: int = 25,
    virtual_size: float = 50,
    window_size: float = 20,
    position: float = 0,
    back_color: str = "#555555",
    bar_color: str = "bright_magenta",
    ascii_only: bool = False,
    vertical: bool = True,
) -> list[Segment]:

    if ascii_only:
        bars = ["|", "|", "|", "|", "|", "|", "|", "|", "|"]
    else:
        bars = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

    back = Color.parse(back_color)
    bar = Color.parse(bar_color)

    _Segment = Segment
    _Style = Style
    segments = [_Segment(" ", _Style(bgcolor=back))] * int(size)

    step_size = virtual_size / size

    start = int(position / step_size * 8)
    end = start + int(window_size / step_size * 8)

    start_index, start_bar = divmod(start, 8)
    end_index, end_bar = divmod(end, 8)

    if window_size / step_size <= 1:
        if start_index < len(segments):
            segments[start_index] = _Segment(" ", _Style(bgcolor=bar))
    else:
        segments[start_index:end_index] = [_Segment(" ", _Style(bgcolor=bar))] * (
            end_index - start_index
        )

        if start_index < len(segments):
            segments[start_index] = _Segment(
                bars[7 - start_bar], _Style(bgcolor=back, color=bar)
            )
        if end_index < len(segments):
            segments[end_index] = _Segment(
                bars[7 - end_bar], _Style(color=back, bgcolor=bar)
            )

    return segments


if __name__ == "__main__":
    from rich.console import Console
    from rich.segment import Segments

    console = Console()

    bar = render_bar(
        size=10,
        virtual_size=100,
        window_size=20,
        position=80,
        vertical=True,
        ascii_only=False,
    )

    console.print(Segments(bar, new_lines=True))
