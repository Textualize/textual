"""Provides the base code and implementations of toggle widgets.

In particular it provides `Checkbox`, `RadioButton` and `RadioSet`.
"""

from __future__ import annotations

from typing import ClassVar

from rich.text import Text, TextType

from ..app import RenderResult
from ..binding import Binding, BindingType
from ..reactive import reactive
from ._static import Static


class ToggleButton(Static):
    """Base toggle button widget."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter,space", "toggle", "Toggle", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter,space | Toggle the value. |
    """

    button_prefix: reactive[TextType] = reactive[TextType]("[")
    """The character for the left side of the toggle button."""

    button_suffix: reactive[TextType] = reactive[TextType]("]")
    """The character for the right side of the toggle button."""

    button_off: reactive[TextType] = reactive[TextType](" ")
    """The character used to signify that the button is off."""

    button_on: reactive[TextType] = reactive[TextType]("X")
    """The character used to signify that the button is on."""

    label: reactive[TextType] = reactive[TextType]("")
    """The label that describes the toggle."""

    value: reactive[bool] = reactive(False)
    """The value of the button. `True` for on, `False` for off."""

    def __init__(
        self,
        label: TextType,
        value: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Initialise the toggle.

        Args:
            value: The initial value of the toggle. Defaults to `False`.
            name: The name of the toggle.
            id: The ID of the toggle in the DOM.
            classes: The CSS classes of the toggle.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.label = label
        self.value = value

    @property
    def _button(self) -> Text:
        """The button, reflecting the current value."""
        return Text.assemble(
            self.button_prefix,
            (self.button_on if self.value else self.button_off),
            self.button_suffix,
        )

    def render(self) -> RenderResult:
        """Render the content of the widget.

        Returns:
            The content to render for the widget.
        """
        # TODO: Built a renderable properly.
        return self._button + (" " if self.label else "") + f"{self.label}"

    def toggle(self) -> None:
        """Toggle the value of the widget."""
        self.value = not self.value

    def action_toggle(self) -> None:
        """Toggle the value of the widget."""
        self.toggle()

    def on_click(self) -> None:
        """Toggle the value of the widget."""
        self.toggle()
