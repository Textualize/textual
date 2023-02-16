"""Provides a radio button widget."""

from __future__ import annotations

from ._toggle import ToggleButton


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
