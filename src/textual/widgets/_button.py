from __future__ import annotations

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.style import StyleType

from .. import events
from ..message import Message
from ..reactive import Reactive
from ..widget import Widget


class ButtonPressed(Message, bubble=True):
    pass


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
        super().__init__(name=name)
        self.name = name or str(label)
        self.button_style = style

        self.label = label

    label: Reactive[RenderableType] = Reactive("")

    def render(self) -> RenderableType:
        return ButtonRenderable(self.label, style=self.button_style)

    async def on_click(self, event: events.Click) -> None:
        event.prevent_default().stop()
        await self.emit(ButtonPressed(self))
