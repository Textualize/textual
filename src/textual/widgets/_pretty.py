from __future__ import annotations

from typing import Any
from rich.pretty import Pretty as PrettyRenderable

from ..widget import Widget


class Pretty(Widget):
    DEFAULT_CSS = """
    Static {
        height: auto;
    }
    """

    def __init__(
        self,
        object: Any,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
        )
        self._renderable = PrettyRenderable(object)

    def render(self) -> PrettyRenderable:
        return self._renderable

    def update(self, object: Any) -> None:
        self._renderable = PrettyRenderable(object)
        self.refresh(layout=True)
