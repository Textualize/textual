from __future__ import annotations


import logging

from rich.repr import rich_repr, RichReprResult
from rich.color import Color
from rich.style import Style
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.segment import Segment, Segments
from rich.style import Style, StyleType

log = logging.getLogger("rich")

from . import events
from .message import Message
from .widget import Reactive, Widget


class ScrollUp(Message, bubble=True):
    pass


class ScrollDown(Message, bubble=True):
    pass


class ScrollBarRender:
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

        background_meta = {"background": True}
        foreground_meta = {"background": False}

        back_segment = Segment(blank, _Style(bgcolor=back, meta=background_meta))
        segments = [back_segment] * int(size)
        if window_size and size and virtual_size:
            step_size = virtual_size / size

            start = int(position / step_size * 8)
            end = start + max(8, int(window_size / step_size * 8))

            start_index, start_bar = divmod(start, 8)
            end_index, end_bar = divmod(end, 8)

            segments[start_index:end_index] = [
                _Segment(blank, _Style(bgcolor=bar, meta=foreground_meta))
            ] * (end_index - start_index)

            if start_index < len(segments):
                segments[start_index] = _Segment(
                    bars[7 - start_bar] * width_thickness,
                    _Style(bgcolor=back, color=bar, meta=foreground_meta)
                    if vertical
                    else _Style(bgcolor=bar, color=back, meta=foreground_meta),
                )
            if end_index < len(segments):
                segments[end_index] = _Segment(
                    bars[7 - end_bar] * width_thickness,
                    _Style(bgcolor=bar, color=back, meta=foreground_meta)
                    if vertical
                    else _Style(bgcolor=back, color=bar, meta=foreground_meta),
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


@rich_repr
class ScrollBar(Widget):
    def __init__(self, vertical: bool = True, name: str | None = None) -> None:
        self.vertical = vertical
        super().__init__(name=name)

    virtual_size: Reactive[int] = Reactive(100)
    window_size: Reactive[int] = Reactive(20)
    position: Reactive[int] = Reactive(0)
    mouse_over: Reactive[bool] = Reactive(False)

    def __rich_repr__(self) -> RichReprResult:
        yield "virtual_size", self.virtual_size
        yield "window_size", self.window_size
        yield "position", self.position

    __rich_repr__.angular = True

    def render(self) -> RenderableType:
        return ScrollBarRender(
            virtual_size=self.virtual_size,
            window_size=self.window_size,
            position=self.position,
            vertical=self.vertical,
            style="bright_magenta on #555555"
            if self.mouse_over
            else "bright_magenta on #444444",
        )

    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False


if __name__ == "__main__":
    from rich.console import Console
    from rich.segment import Segments

    console = Console()
    bar = ScrollBarRender()

    console.print(ScrollBarRender(position=15.3, thickness=5, vertical=False))
