from __future__ import annotations

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.padding import Padding
from rich.panel import Panel
import rich.repr
from rich.style import StyleType

from ..reactive import Reactive
from ..widget import Widget


class Expand:
    def __init__(self, renderable: RenderableType) -> None:
        self.renderable = renderable

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width
        height = options.height or 1
        yield from console.render(
            self.renderable, options.update_dimensions(width, height)
        )


class ButtonRenderable:
    def __init__(self, label: RenderableType, style: StyleType = "") -> None:
        self.label = label
        self.style = style

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width
        height = options.height or 1

        yield Align.center(
            self.label, vertical="middle", style=self.style, width=width, height=height
        )


class Button(Widget):
    def __init__(
        self,
        label: RenderableType,
        name: str | None = None,
        style: StyleType = "white on dark_blue",
    ):
        self.label = label
        self.name = name or str(label)
        self.style = style
        super().__init__()

    def render(self) -> RenderableType:
        return ButtonRenderable(self.label, style=self.style)
        return Align.center(self.label, vertical="middle", style=self.style)
