from __future__ import annotations

from math import ceil
import logging


from rich.color import Color
from rich.style import Style
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.segment import Segment, Segments
from rich.style import Style, StyleType

log = logging.getLogger("rich")

from .widget import Widget


class ScrollBar:
    def __init__(
        self,
        virtual_size: int = 100,
        window_size: int = 25,
        position: float = 0,
        thickness: int = 1,
        vertical: bool = True,
        style: StyleType = "bright_magenta on #555555",
    ) -> None:
        self.virtual_size = virtual_size
        self.window_size = window_size
        self.position = position
        self.thickness = thickness
        self.vertical = vertical
        self.style = style

    @classmethod
    def render_bar(
        cls,
        size: int = 25,
        virtual_size: float = 50,
        window_size: float = 20,
        position: float = 0,
        ascii_only: bool = False,
        thickness: int = 1,
        vertical: bool = True,
        back_color: Color = Color.parse("#555555"),
        bar_color: Color = Color.parse("bright_magenta"),
    ) -> Segments:

        if vertical:
            if ascii_only:
                bars = ["|", "|", "|", "|", "|", "|", "|", "|"]
            else:
                bars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        else:
            if ascii_only:
                bars = ["-", "-", "-", "-", "-", "-", "-", "-"]
            else:
                bars = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

        back = back_color
        bar = bar_color

        width_thickness = thickness if vertical else 1

        _Segment = Segment
        _Style = Style
        blank = " " * width_thickness
        segments = [_Segment(blank, _Style(bgcolor=back))] * int(size)

        step_size = virtual_size / size

        start = int(position / step_size * 8)
        end = start + max(8, int(window_size / step_size * 8))

        start_index, start_bar = divmod(start, 8)
        end_index, end_bar = divmod(end, 8)

        segments[start_index:end_index] = [_Segment(blank, _Style(bgcolor=bar))] * (
            end_index - start_index
        )

        if start_index < len(segments):
            segments[start_index] = _Segment(
                bars[7 - start_bar] * width_thickness,
                _Style(bgcolor=back, color=bar)
                if vertical
                else _Style(bgcolor=bar, color=back),
            )
        if end_index < len(segments):
            segments[end_index] = _Segment(
                bars[7 - end_bar] * width_thickness,
                _Style(bgcolor=bar, color=back)
                if vertical
                else _Style(bgcolor=back, color=bar),
            )
        if vertical:
            return Segments(segments, new_lines=True)
        else:
            return Segments((segments + [_Segment.line()]) * thickness, new_lines=False)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        size = (
            (options.height or console.height)
            if self.vertical
            else (options.max_width or console.width)
        )
        thickness = (
            (options.max_width or console.width)
            if self.vertical
            else (options.height or console.height)
        )

        _style = console.get_style(self.style)

        bar = self.render_bar(
            size=size,
            window_size=self.window_size,
            virtual_size=self.virtual_size,
            position=self.position,
            vertical=self.vertical,
            thickness=thickness,
            back_color=_style.bgcolor or Color.parse("#555555"),
            bar_color=_style.color or Color.parse("bright_magenta"),
        )
        yield bar


if __name__ == "__main__":
    from rich.console import Console
    from rich.segment import Segments

    console = Console()
    bar = ScrollBar()

    console.print(ScrollBar(position=15.3, thickness=5, vertical=False))
