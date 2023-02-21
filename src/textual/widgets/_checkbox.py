"""Provides a check box widget."""

from __future__ import annotations

from ._toggle import ToggleButton


class Checkbox(ToggleButton):
    """A check box widget that represents a boolean value."""

    class Selected(ToggleButton.Selected):
        """Posted when the user selects the button."""

        # https://github.com/Textualize/textual/issues/1814
        namespace = "checkbox"

    class Changed(ToggleButton.Changed):
        """Posted when the value of the checkbox changes."""

        # https://github.com/Textualize/textual/issues/1814
        namespace = "checkbox"

    def __init__(
        self,
        label: str,
        value: bool = False,
        button_first: bool = True,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the radio button.

        Args:
            label: The label for the toggle.
            value: The initial value of the checkbox. Defaults to `False`.
            button_first: Should the button come before the label, or after?
            name: The name of the checkbox.
            id: The ID of the checkbox in the DOM.
            classes: The CSS classes of the checkbox.
            disabled: Whether the button is disabled or not.
        """
        super().__init__(
            label,
            value,
            button_first,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.button_on = "✓"
