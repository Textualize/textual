from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import RenderableType
from rich.protocol import is_renderable
from rich.text import Text

if TYPE_CHECKING:
    from textual.app import RenderResult

from textual.errors import RenderError
from textual.widget import Widget


def _check_renderable(renderable: object):
    """Check if a renderable conforms to the Rich Console protocol
    (https://rich.readthedocs.io/en/latest/protocol.html)

    Args:
        renderable: A potentially renderable object.

    Raises:
        RenderError: If the object can not be rendered.
    """
    if not is_renderable(renderable):
        raise RenderError(
            f"unable to render {renderable!r}; a string, Text, or other Rich renderable is required"
        )


class Static(Widget, inherit_bindings=False):
    """A widget to display simple static content, or use as a base class for more complex widgets.

    Args:
        renderable: A Rich renderable, or string containing console markup.
        expand: Expand content if required to fill container.
        shrink: Shrink content if required to fill container.
        markup: True if markup should be parsed and rendered.
        name: Name of widget.
        id: ID of Widget.
        classes: Space separated list of class names.
        disabled: Whether the static is disabled or not.
    """

    DEFAULT_CSS = """
    Static {
        height: auto;
    }
    """

    _renderable: RenderableType

    def __init__(
        self,
        renderable: RenderableType = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.expand = expand
        self.shrink = shrink
        self.markup = markup
        self.renderable = renderable
        _check_renderable(renderable)

    @property
    def renderable(self) -> RenderableType:
        return self._renderable or ""

    @renderable.setter
    def renderable(self, renderable: RenderableType) -> None:
        if isinstance(renderable, str):
            if self.markup:
                self._renderable = Text.from_markup(renderable)
            else:
                self._renderable = Text(renderable)
        else:
            self._renderable = renderable
        self.clear_cached_dimensions()

    def render(self) -> RenderResult:
        """Get a rich renderable for the widget's content.

        Returns:
            A rich renderable.
        """
        return self._renderable

    def update(self, renderable: RenderableType = "") -> None:
        """Update the widget's content area with new text or Rich renderable.

        Args:
            renderable: A new rich renderable. Defaults to empty renderable;
        """
        _check_renderable(renderable)
        self.renderable = renderable
        self.refresh(layout=True)
