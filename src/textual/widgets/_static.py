from __future__ import annotations

from rich.console import RenderableType
from rich.padding import Padding, PaddingDimensions
from rich.style import StyleType
from rich.styled import Styled
from ..widget import Widget


class Static(Widget):
    def __init__(
        self,
        renderable: RenderableType,
        name: str | None = None,
        style: StyleType = "",
        padding: PaddingDimensions = 0,
    ) -> None:
        super().__init__(name)
        self.renderable = renderable
        self.style = style
        self.padding = padding

    def render(self) -> RenderableType:
        renderable = self.renderable
        if self.padding:
            renderable = Padding(renderable, self.padding)
        return Styled(renderable, self.style)

    async def update(self, renderable: RenderableType) -> None:
        self.renderable = renderable
        self.require_repaint()
