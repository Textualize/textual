"""Provides a RadioSet widget, which groups radio buttons."""

from __future__ import annotations

from ..containers import Container
from ..widget import WidgetError
from ._radio_button import RadioButton


class RadioSet(Container):
    """Widget for grouping a collection of radio buttons into a set."""

    class ButtonTypeError(WidgetError):
        """Type of error thrown if an unknown button type is passed."""

    def __init__(
        self,
        *buttons: str | RadioButton,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialise the radio set.

        Args:
            buttons: A collection of labels or `RadioButton`s to group together.
            name: The name of the radio set.
            id: The ID of the radio set in the DOM.
            classes: The CSS classes of the radio set.

        Note:
            When a `str` label is provided, a `RadioButton` will be created from it.
        """

        # Be sure we've only been handed strings or radio buttons. This is a
        # container that can't contain anything else.
        for button in buttons:
            if not isinstance(button, (str, RadioButton)):
                raise self.ButtonTypeError(
                    f"{button!r} is not of type `str` or `RadioButton`"
                )

        # Build the internal list of buttons. Here, if we're given a
        # RadioButton, we use it as-is; otherwise we spin one up from the
        # given string. We could, of course, just use the children property
        # to do this as we're guaranteeing that everything within here is a
        # RadioButton, but doing it this way makes subsequent type issues
        # less of a problem *and* it's a guard against a developer doing a
        # sneaky mount on us after the fact.
        self._buttons = [
            (button if isinstance(button, RadioButton) else RadioButton(button))
            for button in buttons
        ]

        super().__init__(*self._buttons, name=name, id=id, classes=classes)

    def on_mount(self) -> None:
        """Set up the radio group for use after the DOM is loaded."""
        # The assumption here is that we should always start out with at
        # least one button pressed. So, if there isn't a pressed button...
        if self._buttons and not any(button.value for button in self._buttons):
            # ...press the first one.
            self._buttons[0].value = True

    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        """Respond to the value of a button in the set being changed.

        Args:
            event: The event.
        """
        # If the button is changing to be the pressed button...
        if event.input.value:
            # ...look for the button that was previously the pressed one and
            # unpress it.
            for button in self._buttons:
                if button.value and button != event.input:
                    button.value = False
                    break
