"""Provides a radio button widget."""

from __future__ import annotations

from ._toggle import ToggleButton


class RadioButton(ToggleButton):
    """A radio button widget that represents a boolean value.

    TODO: Mention that this is best used in a RadioSet (yet to be added).
    """

    class Changed(ToggleButton.Changed):
        """Posted when the value of the radio button changes."""

        # https://github.com/Textualize/textual/issues/1814
        namespace = "radio_button"

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
            value: The initial value of the radio button. Defaults to `False`.
            button_first: Should the button come before the label, or after?
            name: The name of the radio button.
            id: The ID of the radio button in the DOM.
            classes: The CSS classes of the radio button.
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
        self.button_inner = "⏺"
