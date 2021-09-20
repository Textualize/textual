from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment, SegmentLines
from rich.style import StyleType

from .widget import Widget


class BackgroundRenderable:
    def __init__(self, style: StyleType) -> None:
        self.style = style

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:

        width = options.max_width
        height = options.height or console.height
        style = console.get_style(self.style)
        blank_segment = Segment(" " * width, style)
        lines = SegmentLines([[blank_segment]] * height, new_lines=True)
        yield lines


class Background(Widget):
    def __init__(self, style: StyleType = "on blue") -> None:
        self.background_style = style

    def render(self) -> BackgroundRenderable:
        return BackgroundRenderable(self.background_style)
