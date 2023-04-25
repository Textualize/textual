"""Provides a RadioSet widget, which groups radio buttons."""

from __future__ import annotations

from typing import ClassVar

import rich.repr

from ..binding import Binding, BindingType
from ..containers import Container
from ..events import Mount
from ..message import Message
from ._radio_button import RadioButton


class RadioSet(Container):
    """Widget for grouping a collection of radio buttons into a set.

    When a collection of [`RadioButton`][textual.widgets.RadioButton]s are
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

    RadioSet:focus-within {
        border: round $accent;
    }

    App.-light-mode RadioSet {
        border: round #CCC;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("down,right", "next_button", "", show=False),
        Binding("shift+tab", "breakout_previous", "", show=False),
        Binding("tab", "breakout_next", "", show=False),
        Binding("up,left", "previous_button", "", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | left, up | Select the previous radio button in the set. |
    | right, down | Select the next radio button in the set. |
    | shift+tab | Move focus to the previous focusable widget relative to the set. |
    | tab | Move focus to the next focusable widget relative to the set. |
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
            """A reference to the [`RadioSet`][textual.widgets.RadioSet] that was changed."""
            self.pressed = pressed
            """The [`RadioButton`][textual.widgets.RadioButton] that was pressed to make the change."""
            self.index = radio_set.pressed_index
            """The index of the [`RadioButton`][textual.widgets.RadioButton] that was pressed to make the change."""

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
            buttons: A collection of labels or [`RadioButton`][textual.widgets.RadioButton]s to group together.
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

    def _on_mount(self, _: Mount) -> None:
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

    def _on_radio_button_changed(self, event: RadioButton.Changed) -> None:
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
        """The currently-pressed [`RadioButton`][textual.widgets.RadioButton], or `None` if none are pressed."""
        return self._pressed_button

    @property
    def pressed_index(self) -> int:
        """The index of the currently-pressed [`RadioButton`][textual.widgets.RadioButton], or -1 if none are pressed."""
        return (
            self._nodes.index(self._pressed_button)
            if self._pressed_button is not None
            else -1
        )

    def action_previous_button(self) -> None:
        """Navigate to the previous button in the set.

        Note that this will wrap around to the end if at the start.
        """
        if self.children:
            if self.screen.focused == self.children[0]:
                self.screen.set_focus(self.children[-1])
            else:
                self.screen.focus_previous()

    def action_next_button(self) -> None:
        """Navigate to the next button in the set.

        Note that this will wrap around to the start if at the end.
        """
        if self.children:
            if self.screen.focused == self.children[-1]:
                self.screen.set_focus(self.children[0])
            else:
                self.screen.focus_next()

    def action_breakout_previous(self) -> None:
        """Break out of the radio set to the previous widget in the focus chain."""
        if self.children:
            self.screen.set_focus(self.children[0])
        self.screen.focus_previous()

    def action_breakout_next(self) -> None:
        """Break out of the radio set to the next widget in the focus chain."""
        if self.children:
            self.screen.set_focus(self.children[-1])
        self.screen.focus_next()
