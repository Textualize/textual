from __future__ import annotations

from typing import cast

from rich.align import Align, AlignMethod
from rich.console import RenderableType

from textual.geometry import Size

from ..css.types import AlignHorizontal
from ..geometry import Size
from ..reactive import reactive
from ..renderables.digits import Digits as DigitsRenderable
from ..widget import Widget


class Digits(Widget):
    """A widget to display numerical values using a 3x3 grid of unicode characters."""

    DEFAULT_CSS = """
    Digits {
        width: 1fr;
        height: 3;
        text-align: left;
        text-style: bold;
    }
    """

    def __init__(
        self,
        value: str = "0",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize digits

        Args:
            label: The text that appears within the button.
            variant: The variant of the button.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.value = value

    def update(self, new_value: str) -> None:
        """Update the Digits with a new value.

        Args:
            new_value: New value to display.
        """
        layout_required = len(new_value) != len(self.value) or (
            DigitsRenderable.get_width(self.value)
            != DigitsRenderable.get_width(new_value)
        )
        self.value = new_value
        self.refresh(layout=layout_required)

    def render(self) -> RenderableType:
        """Render digits."""
        rich_style = self.rich_style
        digits = DigitsRenderable(self.value, rich_style)
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
        return DigitsRenderable.get_width(self.value)

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


if __name__ == "__main__":
    from time import time

    from textual.app import App, ComposeResult

    class DigitApp(App):
        def on_ready(self) -> None:
            digits = self.query_one(Digits)
            number = 2**32

            def update():
                nonlocal number
                number += 1
                digits.update("123,232.23")

            self.set_interval(1 / 10, update)

        def compose(self) -> ComposeResult:
            yield Digits()

    app = DigitApp()
    app.run()
