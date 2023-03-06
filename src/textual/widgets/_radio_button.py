"""Provides a radio button widget."""

from __future__ import annotations

from ._toggle_button import ToggleButton


class RadioButton(ToggleButton):
    """A radio button widget that represents a boolean value.

    Note:
        A `RadioButton` is best used within a [RadioSet][textual.widgets.RadioSet].
    """

    BUTTON_INNER = "⏺"
    """The character used for the inside of the button."""

    class Changed(ToggleButton.Changed):
        """Posted when the value of the radio button changes.

        This message can be handled using an `on_radio_button_changed` method.
        """

        # https://github.com/Textualize/textual/issues/1814
        namespace = "radio_button"

        @property
        def radio_button(self) -> RadioButton:
            """The radio button that was changed."""
            assert isinstance(self._toggle_button, RadioButton)
            return self._toggle_button
