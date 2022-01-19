from __future__ import annotations

from rich.console import Console, ConsoleOptions
from rich.segment import Segment
from rich.style import StyleType


class Blank:
    """
    Render an empty rectangle.

    Args:
        style (StyleType): Style to apply to the box.
        width (int, optional): Width of the box in number of cells. Will expand to fit parent if ``None``.
        height (int, optional): Height of the box in number of cells. Will expand to fit parent if ``None``.
    """

    def __init__(
        self, style: StyleType, width: int | None = None, height: int | None = None
    ):
        self.style = style
        self.width = width
        self.height = height

    def __rich_console__(self, console: Console, console_options: ConsoleOptions):
        render_width = self.width or console_options.max_width
        render_height = (
            self.height or console_options.height or console_options.max_height
        )
        style = console.get_style(self.style)
        for _ in range(render_height):
            yield Segment(" " * render_width + "\n", style)
