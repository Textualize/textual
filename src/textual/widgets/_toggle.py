"""Provides the base code and implementations of toggle widgets.

In particular it provides `Checkbox`, `RadioButton` and `RadioSet`.
"""

from __future__ import annotations

from typing import ClassVar

from rich.console import RenderableType

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

    button_prefix: reactive[RenderableType] = reactive[RenderableType]("[")
    """The character for the left side of the toggle button."""

    button_suffix: reactive[RenderableType] = reactive[RenderableType]("]")
    """The character for the right side of the toggle button."""

    button_off: reactive[RenderableType] = reactive[RenderableType](" ")
    """The character used to signify that the button is off."""

    button_on: reactive[RenderableType] = reactive[RenderableType]("X")
    """The character used to signify that the button is on."""

    label: reactive[RenderableType] = reactive[RenderableType]("")
    """The label that describes the toggle."""

    value: reactive[bool] = reactive(False)
    """The value of the button. `True` for on, `False` for off."""

    def __init__(
        self,
        label: str,
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

    def render(self) -> RenderResult:
        """Render the content of the widget."""
        # TODO: Built a renderable properly.
        return (
            f"{self.button_prefix}{self.button_on if self.value else self.button_off}{self.button_suffix}"
            + (" " if self.label else "")
            + f"{self.label}"
        )

    def action_toggle(self) -> None:
        """Toggle the value of the widget."""
        self.value = not self.value

    def on_click(self) -> None:
        """Toggle the value of the widget."""
        self.action_toggle()


class Checkbox(ToggleButton):
    pass


class RadioButton(ToggleButton):
    def __init__(
        self,
        label: str,
        value: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Initialise the radio button.

        Args:
            value: The initial value of the radio button. Defaults to `False`.
            name: The name of the radio button.
            id: The ID of the radio button in the DOM.
            classes: The CSS classes of the radio button.
        """
        super().__init__(label, value, name=name, id=id, classes=classes)
        self.button_prefix = "("
        self.button_suffix = ")"
        self.button_on = "*"
        self.button_off = " "
