from __future__ import annotations

from rich.console import RenderableType
from rich.style import StyleType
from rich.styled import Styled
from ..widget import Widget


class Static(Widget):
    def __init__(
        self, renderable: RenderableType, name: str | None = None, style: StyleType = ""
    ) -> None:
        super().__init__(name)
        self.renderable = renderable
        self.style = style

    def render(self) -> RenderableType:
        return Styled(self.renderable, self.style)

    async def update(self, renderable: RenderableType) -> None:
        self.renderable = renderable
        self.require_repaint()
