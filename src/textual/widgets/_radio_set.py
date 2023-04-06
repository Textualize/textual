"""Provides a RadioSet widget, which groups radio buttons."""

from __future__ import annotations

import rich.repr

from ..containers import Container
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

    @rich.repr.auto
    class Changed(Message, bubble=True):
        """Posted when the pressed button in the set changes.

        This message can be handled using an `on_radio_set_changed` method.
        """

        def __init__(self, radio_set: RadioSet, pressed: RadioButton) -> None:
            """Initialise the message.

            Args:
                pressed: The radio button that was pressed.
            """
            super().__init__()
            self.radio_set = radio_set
            """A reference to the `RadioSet` that was changed."""
            self.pressed = pressed
            """The `RadioButton` that was pressed to make the change."""
            self.index = radio_set.pressed_index
            """The index of the `RadioButton` that was pressed to make the change."""

        def __rich_repr__(self) -> rich.repr.Result:
            yield "radio_set", self.radio_set
            yield "pressed", self.pressed
            yield "index", self.index

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
        self._pressed_button: RadioButton | None = None
        """Holds the radio buttons we're responsible for."""
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

    def on_mount(self) -> None:
        """Perform some processing once mounted in the DOM."""

        # It's possible for the user to pass in a collection of radio
        # buttons, with more than one set to on; they shouldn't, but we
        # can't stop them. So here we check for that and, for want of a
        # better approach, we keep the first one on and turn all the others
        # off.
        switched_on = [button for button in self.query(RadioButton) if button.value]
        with self.prevent(RadioButton.Changed):
            for button in switched_on[1:]:
                button.value = False

        # Keep track of which button is initially pressed.
        if switched_on:
            self._pressed_button = switched_on[0]

    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        """Respond to the value of a button in the set being changed.

        Args:
            event: The event.
        """
        # We're going to consume the underlying radio button events, making
        # it appear as if they don't emit their own, as far as the caller is
        # concerned. As such, stop the event bubbling and also prohibit the
        # same event being sent out if/when we make a value change in here.
        event.stop()
        with self.prevent(RadioButton.Changed):
            # If the message pertains to a button being clicked to on...
            if event.radio_button.value:
                # If there's a button pressed right now and it's not really a
                # case of the user mashing on the same button...
                if (
                    self._pressed_button is not None
                    and self._pressed_button != event.radio_button
                ):
                    self._pressed_button.value = False
                # Make the pressed button this new button.
                self._pressed_button = event.radio_button
                # Emit a message to say our state has changed.
                self.post_message(self.Changed(self, event.radio_button))
            else:
                # We're being clicked off, we don't want that.
                event.radio_button.value = True

    @property
    def pressed_button(self) -> RadioButton | None:
        """The currently-pressed button, or `None` if none are pressed."""
        return self._pressed_button

    @property
    def pressed_index(self) -> int:
        """The index of the currently-pressed button, or -1 if none are pressed."""
        return (
            self._nodes.index(self._pressed_button)
            if self._pressed_button is not None
            else -1
        )
