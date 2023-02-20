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

    def on_radio_button_selected(self, event: RadioButton.Selected) -> None:
        """Respond to a radio button in the set being selected be the user.

        Args:
            event: The event being raised.
        """
        # For each of the buttons we're responsible for...
        for button in self._buttons:
            # ...if it's on and it's not the selected button...
            if button.value and button != event.input:
                # ...turn it off.
                button.value = False
                break
