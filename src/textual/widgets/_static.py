from __future__ import annotations

from typing import TYPE_CHECKING

from rich.protocol import is_renderable

if TYPE_CHECKING:
    from textual.app import RenderResult

from textual.errors import RenderError
from textual.visual import Visual, VisualType, visualize
from textual.widget import Widget


def _check_renderable(renderable: object):
    """Check if a renderable conforms to the Rich Console protocol
    (https://rich.readthedocs.io/en/latest/protocol.html)

    Args:
        renderable: A potentially renderable object.

    Raises:
        RenderError: If the object can not be rendered.
    """
    if not is_renderable(renderable) and not hasattr(renderable, "visualize"):
        raise RenderError(
            f"unable to render {renderable.__class__.__name__!r} type; must be a str, Text, Rich renderable oor Textual Visual instance"
        )


class Static(Widget, inherit_bindings=False):
    """A widget to display simple static content, or use as a base class for more complex widgets.

    Args:
        content: A Content object, Rich renderable, or string containing console markup.
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

    _renderable: VisualType

    def __init__(
        self,
        content: VisualType = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name, id=id, classes=classes, disabled=disabled, markup=markup
        )
        self.expand = expand
        self.shrink = shrink
        self._content = content
        self._visual: Visual | None = None

    @property
    def visual(self) -> Visual:
        if self._visual is None:
            self._visual = visualize(self, self._content, markup=self._render_markup)
        return self._visual

    @property
    def renderable(self) -> VisualType:
        return self._content or ""

    # TODO: Should probably be renamed to `content`.
    @renderable.setter
    def renderable(self, renderable: VisualType) -> None:
        self._renderable = renderable
        self._visual = None
        self.clear_cached_dimensions()

    def render(self) -> RenderResult:
        """Get a rich renderable for the widget's content.

        Returns:
            A rich renderable.
        """
        return self.visual

    def update(self, content: VisualType = "") -> None:
        """Update the widget's content area with new text or Rich renderable.

        Args:
            content: New content.
        """

        self._content = content
        self._visual = visualize(self, content, markup=self._render_markup)
        self.refresh(layout=True)
