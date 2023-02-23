"""Provides a radio button widget."""

from ._toggle_button import ToggleButton


class RadioButton(ToggleButton):
    """A radio button widget that represents a boolean value.

    TODO: Mention that this is best used in a RadioSet (yet to be added).
    """

    BUTTON_INNER = "⏺"
    """The character used to for the inside of the button."""

    class Changed(ToggleButton.Changed):
        """Posted when the value of the radio button changes."""

        # https://github.com/Textualize/textual/issues/1814
        namespace = "radio_button"
