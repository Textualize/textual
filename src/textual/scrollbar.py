from __future__ import annotations

from math import ceil
import logging
from typing import Iterable

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
        position: int,
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
    bar_style: Style | None = None,
    back_style: Style | None = None,
    ascii_only: bool = False,
    vertical: bool = True,
) -> list[Segment]:
    if vertical:
        if ascii_only:
            solid = "|"
            half_start = "|"
            half_end = "|"
        else:
            solid = "┃"
            half_start = "╻"
            half_end = "╹"
    else:
        if ascii_only:
            solid = "-"
            half_start = "-"
            half_end = "-"
        else:
            solid = "━"
            half_start = "╺"
            half_end = "╸"

    _bar_style = bar_style or Style.parse("bright_magenta")
    _back_style = back_style or Style.parse("#555555")

    _Segment = Segment

    start_bar_segment = _Segment(half_start, _bar_style)
    end_bar_segment = _Segment(half_end, _bar_style)
    bar_segment = _Segment(solid, _bar_style)

    start_back_segment = _Segment(half_end, _bar_style)
    end_back_segment = _Segment(half_end, _back_style)
    back_segment = _Segment(solid, _back_style)

    segments = [back_segment] * size

    step_size = virtual_size / size

    start = position / step_size
    # end = (position + window_size) / step_size
    end = start + window_size / step_size

    start_index = int(start)
    end_index = start_index + ceil(window_size / step_size)
    bar_height = end_index - start_index

    segments[start_index:end_index] = [bar_segment] * bar_height

    # log.debug("f")
    # sub_position = 1 - (start % 1.0)
    # log.debug("*** sub_position=%r, %r", start, sub_position)

    # if sub_position > 0.5:
    #     segments[start_index - 1] = end_back_segment
    #     segments[start_index] = start_back_segment
    # else:
    #     segments[start_index] = start_bar_segment
    #     # segments[start_index + 1] = start_bar_segment

    # sub_position = end % 1.0
    # if sub_position > 0.5:
    #     segments[end_index] = end_bar_segment
    #     segments[end_index + 1] = back_segment
    # else:
    #     segments[end_index] = start_back_segment
    # segments[end_index + 1] = start_back_segment

    return segments


if __name__ == "__main__":
    from rich.console import Console
    from rich.segment import Segments

    console = Console()

    bar = render_bar(
        size=20,
        virtual_size=100,
        window_size=50,
        position=0,
        vertical=False,
        ascii_only=False,
    )

    console.print(Segments(bar, new_lines=False))
