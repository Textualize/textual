"""Provides a RadioSet widget, which groups radio buttons."""

from __future__ import annotations

from typing import cast

from ..containers import Container
from ..css.query import DOMQuery, QueryError
from ..message import Message
from ._radio_button import RadioButton


class RadioSet(Container):
    """Widget for grouping a collection of radio buttons into a set.

    When a collection of [RadioButton][textual.widgets.RadioButton]s are
    grouped with this widget, they will be treated as a mutually-exclusive
    grouping. If one button is turned on, the previously-on button will be
    turned off.
    """

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

    class Changed(Message, bubble=True):
        """Posted when the pressed button in the set changes.

        This message can be handled using an `on_radio_set_changed` method.
        """

        def __init__(self, sender: RadioSet, pressed: RadioButton) -> None:
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
            # Note: it would be cleaner to use `sender.pressed_index` here,
            # but we can't be 100% sure all of the updates have happened at
            # this point, and so we can't go looking for the index of the
            # pressed button via the normal route. So here we go under the
            # hood.
            self.index = sender._nodes.index(pressed)
            """The index of the `RadioButton` that was pressed to make the change."""

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
            buttons: A collection of labels or [RadioButton][textual.widgets.RadioButton]s to group together.
            name: The name of the radio set.
            id: The ID of the radio set in the DOM.
            classes: The CSS classes of the radio set.
            disabled: Whether the radio set is disabled or not.

        Note:
            When a `str` label is provided, a
            [RadioButton][textual.widgets.RadioButton] will be created from
            it.
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

    def on_mount(self) -> None:
        """Perform some processing once mounted in the DOM."""
        # It's possible for the user to pass in a collection of radio
        # buttons, with more than one set to on. So here we check for that
        # and, for want of a better approach, we keep the first one on and
        # turn all the others off.
        switched_on = self._buttons.filter(".-on")
        if len(switched_on) > 1:
            with self.prevent(RadioButton.Changed):
                for button in switched_on[1:]:
                    button.value = False

    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        """Respond to the value of a button in the set being changed.

        Args:
            event: The event.
        """
        # If the button is changing to be the pressed button...
        if event.input.value:
            # ...send off a message to say that the pressed state has
            # changed.
            self.post_message_no_wait(
                self.Changed(self, cast(RadioButton, event.input))
            )
            # ...then look for the button that was previously the pressed
            # one and unpress it.
            for button in self._buttons.filter(".-on"):
                if button != event.input:
                    button.value = False
                    break
        else:
            # If this leaves us with no buttons checked, disallow that. Note
            # that we stop the current event and (see below) we also prevent
            # another Changed event being emitted. This should all be seen
            # as a non-operation.
            event.stop()
            if not self._buttons.filter(".-on"):
                with self.prevent(RadioButton.Changed):
                    event.input.value = True

    @property
    def pressed_button(self) -> RadioButton | None:
        """The currently-pressed button, or `None` if none are pressed."""
        try:
            return self.query_one("RadioButton.-on", RadioButton)
        except QueryError:
            return None

    @property
    def pressed_index(self) -> int:
        """The index of the currently-pressed button, or -1 if none are pressed."""
        try:
            return self._nodes.index(self.pressed_button)
        except ValueError:
            return -1
