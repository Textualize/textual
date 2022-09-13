from __future__ import annotations

from rich.console import RenderableType
from rich.protocol import is_renderable

from ..reactive import Reactive
from ..errors import RenderError
from ..widget import Widget


def _check_renderable(renderable: object):
    """Check if a renderable conforms to the Rich Console protocol
    (https://rich.readthedocs.io/en/latest/protocol.html)

    Args:
        renderable (object): A potentially renderable object.

    Raises:
        RenderError: If the object can not be rendered.
    """
    if not is_renderable(renderable):
        raise RenderError(
            f"unable to render {renderable!r}; A string, Text, or other Rich renderable is required"
        )


class Static(Widget):
    DEFAULT_CSS = """
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
        _check_renderable(renderable)

    def render(self) -> RenderableType:
        return self.renderable

    def update(self, renderable: RenderableType) -> None:
        _check_renderable(renderable)
        self.renderable = renderable
        self.refresh(layout=True)
