from __future__ import annotations

from rich.console import RenderableType
from rich.protocol import is_renderable
from rich.text import Text

from ..errors import RenderError
from ..widget import Widget


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
            Defaults to "".
        expand: Expand content if required to fill container. Defaults to False.
        shrink: Shrink content if required to fill container. Defaults to False.
        markup: True if markup should be parsed and rendered. Defaults to True.
        name: Name of widget. Defaults to None.
        id: ID of Widget. Defaults to None.
        classes: Space separated list of class names. Defaults to None.
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

    def render(self) -> RenderableType:
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
