"""Provides a RadioSet widget, which groups radio buttons."""

from __future__ import annotations

from ..containers import Container
from ..css.query import DOMQuery, QueryError
from ..message import Message
from ._radio_button import RadioButton
from ._toggle_button import ToggleButton


class RadioSet(Container):
    """Widget for grouping a collection of radio buttons into a set."""

    DEFAULT_CSS = """
    RadioSet {
        border: round #666;
        height: auto;
        width: auto;
    }

    App.-light-mode RadioSet {
        border: round #CCC;
    }
    """

    def __init__(
        self,
        *buttons: str | RadioButton,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the radio set.

        Args:
            buttons: A collection of labels or `RadioButton`s to group together.
            name: The name of the radio set.
            id: The ID of the radio set in the DOM.
            classes: The CSS classes of the radio set.
            disabled: Whether the radio set is disabled or not.

        Note:
            When a `str` label is provided, a `RadioButton` will be created from it.
        """
        super().__init__(
            *[
                (button if isinstance(button, RadioButton) else RadioButton(button))
                for button in buttons
            ],
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @property
    def _buttons(self) -> DOMQuery[RadioButton]:
        """The buttons within the set."""
        return self.query(RadioButton)

    class Changed(Message, bubble=True):
        """Posted when the pressed button in the set changes."""

        def __init__(self, sender: RadioSet, pressed: ToggleButton) -> None:
            """Initialise the message.

            Args:
                sender: The radio set sending the message.
                pressed: The radio button that was pressed.
            """
            super().__init__(sender)
            self.input = sender
            """A reference to the `RadioSet` that was changed."""
            self.pressed = pressed
            """The `RadioButton` that was pressed to make the change."""
            self.index = sender.pressed_index
            """The index of the `RadioButton` that was pressed to make the change."""

    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        """Respond to the value of a button in the set being changed.

        Args:
            event: The event.
        """
        # If the button is changing to be the pressed button...
        if event.input.value:
            # ...send off a message to say that the pressed state has
            # changed.
            self.post_message_no_wait(self.Changed(self, event.input))
            # ...then look for the button that was previously the pressed
            # one and unpress it.
            for button in self._buttons.filter(".-on"):
                if button != event.input:
                    button.value = False
                    break
        else:
            # If this leaves us with no buttons checked, disallow that.
            if not self._buttons.filter(".-on"):
                event.input.value = True

    @property
    def pressed_button(self) -> RadioButton | None:
        """The currently-pressed button, or `None` none are pressed."""
        try:
            return self.query_one("RadioButton.-on", RadioButton)
        except QueryError:
            return None

    @property
    def pressed_index(self) -> int:
        """The index of the currently-pressed button.

        Note:
            If no button is pressed the value will be `-1`.
        """
        try:
            return self._nodes.index(self.pressed_button)
        except ValueError:
            return -1
