from __future__ import annotations

from math import ceil

import rich.repr
from rich.color import Color
from rich.console import ConsoleOptions, RenderResult, RenderableType
from rich.segment import Segment, Segments
from rich.style import Style, StyleType

from textual.reactive import Reactive
from . import events
from ._types import MessageTarget
from .geometry import Offset
from .message import Message
from .widget import Widget


class ScrollMessage(Message, bubble=False):
    pass


@rich.repr.auto
class ScrollUp(ScrollMessage):
    """Message sent when clicking above handle."""


@rich.repr.auto
class ScrollDown(ScrollMessage):
    """Message sent when clicking below handle."""


@rich.repr.auto
class ScrollLeft(ScrollMessage):
    """Message sent when clicking above handle."""


@rich.repr.auto
class ScrollRight(ScrollMessage):
    """Message sent when clicking below handle."""


class ScrollTo(ScrollMessage):
    """Message sent when click and dragging handle."""

    def __init__(
        self,
        sender: MessageTarget,
        x: float | None = None,
        y: float | None = None,
        animate: bool = True,
    ) -> None:
        self.x = x
        self.y = y
        self.animate = animate
        super().__init__(sender)

    def __rich_repr__(self) -> rich.repr.Result:
        yield "x", self.x, None
        yield "y", self.y, None
        yield "animate", self.animate, True


class ScrollBarRender:
    def __init__(
        self,
        virtual_size: int = 100,
        window_size: int = 0,
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
                bars = ["█", "▉", "▊", "▋", "▌", "▍", "▎", "▏"]

        back = back_color
        bar = bar_color

        width_thickness = thickness if vertical else 1

        _Segment = Segment
        _Style = Style
        blank = " " * width_thickness

        foreground_meta = {"@mouse.up": "release", "@mouse.down": "grab"}
        if window_size and size and virtual_size and size != virtual_size:
            step_size = virtual_size / size

            start = int(position / step_size * 8)
            end = start + max(8, int(ceil(window_size / step_size * 8)))

            start_index, start_bar = divmod(start, 8)
            end_index, end_bar = divmod(end, 8)

            upper = {"@click": "scroll_up"}
            lower = {"@click": "scroll_down"}

            upper_back_segment = Segment(blank, _Style(bgcolor=back, meta=upper))
            lower_back_segment = Segment(blank, _Style(bgcolor=back, meta=lower))

            segments = [upper_back_segment] * int(size)
            segments[end_index:] = [lower_back_segment] * (size - end_index)

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
        else:
            style = _Style(bgcolor=back)
            segments = [_Segment(blank, style=style)] * int(size)
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


@rich.repr.auto
class ScrollBar(Widget):
    def __init__(
        self, vertical: bool = True, name: str | None = None, *, thickness: int = 1
    ) -> None:
        self.vertical = vertical
        self.thickness = thickness
        self.grabbed_position: float = 0
        super().__init__(name=name)

    window_virtual_size: Reactive[int] = Reactive(100)
    window_size: Reactive[int] = Reactive(0)
    position: Reactive[int] = Reactive(0)
    mouse_over: Reactive[bool] = Reactive(False)
    grabbed: Reactive[Offset | None] = Reactive(None)

    def __rich_repr__(self) -> rich.repr.Result:
        yield from super().__rich_repr__()
        yield "window_virtual_size", self.window_virtual_size
        yield "window_size", self.window_size
        yield "position", self.position
        if self.thickness > 1:
            yield "thickness", self.thickness

    def render(self, style: Style) -> RenderableType:
        styles = self.parent.styles
        scrollbar_style = Style(
            bgcolor=(
                styles.scrollbar_background_hover.rich_color
                if self.mouse_over
                else styles.scrollbar_background.rich_color
            ),
            color=(
                styles.scrollbar_color_active.rich_color
                if self.grabbed
                else styles.scrollbar_color.rich_color
            ),
        )
        return ScrollBarRender(
            virtual_size=self.window_virtual_size,
            window_size=self.window_size,
            position=self.position,
            thickness=self.thickness,
            vertical=self.vertical,
            style=scrollbar_style,
        )

    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False

    async def action_scroll_down(self) -> None:
        await self.emit(ScrollDown(self) if self.vertical else ScrollRight(self))

    async def action_scroll_up(self) -> None:
        await self.emit(ScrollUp(self) if self.vertical else ScrollLeft(self))

    async def action_grab(self) -> None:
        await self.capture_mouse()

    async def action_released(self) -> None:
        await self.capture_mouse(False)

    async def on_mouse_up(self, event: events.MouseUp) -> None:
        if self.grabbed:
            await self.release_mouse()

    async def on_mouse_capture(self, event: events.MouseCapture) -> None:
        self.grabbed = event.mouse_position
        self.grabbed_position = self.position

    async def on_mouse_release(self, event: events.MouseRelease) -> None:
        self.grabbed = None

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        if self.grabbed and self.window_size:
            x: float | None = None
            y: float | None = None
            if self.vertical:
                y = round(
                    self.grabbed_position
                    + (
                        (event.screen_y - self.grabbed.y)
                        * (self.window_virtual_size / self.window_size)
                    )
                )
            else:
                x = round(
                    self.grabbed_position
                    + (
                        (event.screen_x - self.grabbed.x)
                        * (self.window_virtual_size / self.window_size)
                    )
                )
            await self.emit(ScrollTo(self, x=x, y=y))


if __name__ == "__main__":
    from rich.console import Console

    console = Console()

    thickness = 2
    console.print(f"Bars thickness: {thickness}")

    console.print("Vertical bar:")
    console.print(ScrollBarRender.render_bar(thickness=thickness))

    console.print("Horizontal bar:")
    console.print(ScrollBarRender.render_bar(vertical=False, thickness=thickness))
