from __future__ import annotations

from typing import TYPE_CHECKING, cast

from rich.align import Align, AlignMethod

if TYPE_CHECKING:
    from textual.app import RenderResult
from textual.geometry import Size
from textual.renderables.digits import Digits as DigitsRenderable
from textual.widget import Widget


class Digits(Widget):
    """A widget to display numerical values using a 3x3 grid of unicode characters."""

    DEFAULT_CSS = """
    Digits {
        width: 1fr;
        height: auto;
        text-align: left;        
        box-sizing: border-box;
    }
    """

    def __init__(
        self,
        value: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize a Digits widget.

        Args:
            value: Value to display in widget.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            disabled: Whether the widget is disabled or not.

        """
        if not isinstance(value, str):
            raise TypeError("value must be a str")
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._value = value

    @property
    def value(self) -> str:
        """The current value displayed in the Digits."""
        return self._value

    def update(self, value: str) -> None:
        """Update the Digits with a new value.

        Args:
            value: New value to display.

        Raises:
            ValueError: If the value isn't a `str`.
        """
        if not isinstance(value, str):
            raise TypeError("value must be a str")
        layout_required = len(value) != len(self._value) or (
            DigitsRenderable.get_width(self._value) != DigitsRenderable.get_width(value)
        )
        self._value = value
        self.refresh(layout=layout_required)

    def render(self) -> RenderResult:
        """Render digits."""
        rich_style = self.rich_style
        digits = DigitsRenderable(self._value, rich_style)
        text_align = self.styles.text_align
        align = "left" if text_align not in {"left", "center", "right"} else text_align
        return Align(digits, cast(AlignMethod, align), rich_style)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Called by textual to get the width of the content area.

        Args:
            container: Size of the container (immediate parent) widget.
            viewport: Size of the viewport.

        Returns:
            The optimal width of the content.
        """
        return DigitsRenderable.get_width(self._value)

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Called by Textual to get the height of the content area.

        Args:
            container: Size of the container (immediate parent) widget.
            viewport: Size of the viewport.
            width: Width of renderable.

        Returns:
            The height of the content.
        """
        return 3  # Always 3 lines
