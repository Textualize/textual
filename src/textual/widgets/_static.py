from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import RenderResult

from textual.visual import Visual, VisualType, visualize
from textual.widget import Widget


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
        self.__content = content
        self.__visual: Visual | None = None

    @property
    def visual(self) -> Visual:
        """The visual to be displayed.

        Note that the visual is what is ultimately rendered in the widget, but may not be the
        same object set with the `update` method  or `content` property. For instance, if you
        update with a string, then the visual will be a [Content][textual.content.Content] instance.

        """
        if self.__visual is None:
            self.__visual = visualize(self, self.__content, markup=self._render_markup)
        return self.__visual

    @property
    def content(self) -> VisualType:
        """The original content set in the constructor."""
        return self.__content

    @content.setter
    def content(self, content: VisualType) -> None:
        self.__content = content
        self.__visual = visualize(self, content, markup=self._render_markup)
        self.clear_cached_dimensions()
        self.refresh(layout=True)

    def render(self) -> RenderResult:
        """Get a rich renderable for the widget's content.

        Returns:
            A rich renderable.
        """
        return self.visual

    def update(self, content: VisualType = "", *, layout: bool = True) -> None:
        """Update the widget's content area with a string, a Visual (such as [Content][textual.content.Content]), or a [Rich renderable](https://rich.readthedocs.io/en/latest/protocol.html).

        Args:
            content: New content.
            layout: Also perform a layout operation (set to `False` if you are certain the size won't change).
        """

        self.__content = content
        self.__visual = visualize(self, content, markup=self._render_markup)
        self.refresh(layout=layout)
