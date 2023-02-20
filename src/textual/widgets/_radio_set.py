"""Provides a RadioSet widget, which groups radio buttons."""

from __future__ import annotations

from ..containers import Container
from ._radio_button import RadioButton


class RadioSet(Container):
    """Widget for grouping a collection of radio buttons into a set."""

    def __init__(self, *buttons: str | RadioButton) -> None:
        """Initialise the radio set.

        Args:
            buttons: A collection of labels or `RadioButton`s to group together.

        Note:
            When a `str` label is provided, a `RadioButton` will be created from it.
        """
        self._buttons = [
            (button if isinstance(button, RadioButton) else RadioButton(button))
            for button in buttons
        ]
        super().__init__(*self._buttons)

    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        """Respond to the value of a button in the set being changed.

        Args:
            event: The event.
        """
        # If the button is changing to be the pressed button...
        if event.input.value:
            # ...look the button that was previously the pressed one and
            # unpress it.
            for button in self._buttons:
                if button.value and button != event.input:
                    button.value = False
                    break
