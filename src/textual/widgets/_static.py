from __future__ import annotations

from rich.console import RenderableType
from rich.style import Style

from ..widget import Widget


class Static(Widget):
    CSS = """
    Static {
        height: auto;
    }
    """

    def __init__(
        self,
        renderable: RenderableType = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.renderable = renderable

    def render(self) -> RenderableType:
        return self.renderable

    def update(self, renderable: RenderableType) -> None:
        self.renderable = renderable
        self.refresh(layout=True)
