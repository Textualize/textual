from __future__ import annotations

from rich.console import RenderableType
from ..widget import Widget


class Static(Widget):
    def __init__(self, renderable: RenderableType, name: str | None = None) -> None:
        super().__init__(name)
        self.renderable = renderable

    def render(self) -> RenderableType:
        return self.renderable
