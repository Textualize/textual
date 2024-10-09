"""Provides a radio button widget."""

from __future__ import annotations

from textual.widgets._toggle_button import ToggleButton


class RadioButton(ToggleButton):
    """A radio button widget that represents a boolean value.

    Note:
        A `RadioButton` is best used within a [RadioSet][textual.widgets.RadioSet].
    """

    BUTTON_INNER = "\u25cf"
    """The character used for the inside of the button."""

    class Changed(ToggleButton.Changed):
        """Posted when the value of the radio button changes.

        This message can be handled using an `on_radio_button_changed` method.
        """

        @property
        def radio_button(self) -> RadioButton:
            """The radio button that was changed."""
            assert isinstance(self._toggle_button, RadioButton)
            return self._toggle_button

        @property
        def control(self) -> RadioButton:
            """Alias for [Changed.radio_button][textual.widgets.RadioButton.Changed.radio_button]."""
            return self.radio_button
