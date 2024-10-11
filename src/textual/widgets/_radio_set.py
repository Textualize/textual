"""Provides a RadioSet widget, which groups radio buttons."""

from __future__ import annotations

from typing import ClassVar, Optional

import rich.repr
from rich.console import RenderableType

from textual import _widget_navigation
from textual.binding import Binding, BindingType
from textual.containers import VerticalScroll
from textual.events import Click, Mount
from textual.message import Message
from textual.reactive import var
from textual.widgets._radio_button import RadioButton


class RadioSet(VerticalScroll, can_focus=True, can_focus_children=False):
    """Widget for grouping a collection of radio buttons into a set.

    When a collection of [`RadioButton`][textual.widgets.RadioButton]s are
    grouped with this widget, they will be treated as a mutually-exclusive
    grouping. If one button is turned on, the previously-on button will be
    turned off.
    """

    DEFAULT_CSS = """
    RadioSet {
        border: tall transparent;
        background: $boost;
        padding: 0 1 0 0;
        height: auto;
        width: auto;
    }

    RadioSet:focus {
        border: tall $accent;
    }

    /* The following rules/styles mimic similar ToggleButton:focus rules in
     * ToggleButton. If those styles ever get updated, these should be too.
     */

    RadioSet > RadioButton {
        background: transparent;
        border: none;
        padding: 0 1;
    }

    RadioSet:focus > RadioButton.-selected > .toggle--label {
        text-style: underline;
    }

    RadioSet:focus ToggleButton.-selected > .toggle--button {
        background: $foreground 25%;
    }

    RadioSet:focus > RadioButton.-on.-selected > .toggle--button {
        background: $foreground 25%;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("down,right", "next_button", "Next option", show=False),
        Binding("enter,space", "toggle_button", "Toggle", show=False),
        Binding("up,left", "previous_button", "Previous option", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter, space | Toggle the currently-selected button. |
    | left, up | Select the previous radio button in the set. |
    | right, down | Select the next radio button in the set. |
    """

    _selected: var[int | None] = var[Optional[int]](None)
    """The index of the currently-selected radio button."""

    @rich.repr.auto
    class Changed(Message):
        """Posted when the pressed button in the set changes.

        This message can be handled using an `on_radio_set_changed` method.
        """

        ALLOW_SELECTOR_MATCH = {"pressed"}
        """Additional message attributes that can be used with the [`on` decorator][textual.on]."""

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

        @property
        def control(self) -> RadioSet:
            """A reference to the [`RadioSet`][textual.widgets.RadioSet] that was changed.

            This is an alias for [`Changed.radio_set`][textual.widgets.RadioSet.Changed.radio_set]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.radio_set

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
        tooltip: RenderableType | None = None,
    ) -> None:
        """Initialise the radio set.

        Args:
            buttons: The labels or [`RadioButton`][textual.widgets.RadioButton]s to group together.
            name: The name of the radio set.
            id: The ID of the radio set in the DOM.
            classes: The CSS classes of the radio set.
            disabled: Whether the radio set is disabled or not.
            tooltip: Optional tooltip.

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
        if tooltip is not None:
            self.tooltip = tooltip

    def _on_mount(self, _: Mount) -> None:
        """Perform some processing once mounted in the DOM."""

        # If there are radio buttons, select the first available one.
        self.action_next_button()

        # Get all the buttons within us; we'll be doing a couple of things
        # with that list.
        buttons = list(self.query(RadioButton))

        # RadioButtons can have focus, by default. But we're going to take
        # that over and handle movement between them. So here we tell them
        # all they can't focus.
        for button in buttons:
            button.can_focus = False

        # It's possible for the user to pass in a collection of radio
        # buttons, with more than one set to on; they shouldn't, but we
        # can't stop them. So here we check for that and, for want of a
        # better approach, we keep the first one on and turn all the others
        # off.
        switched_on = [button for button in buttons if button.value]
        with self.prevent(RadioButton.Changed):
            for button in switched_on[1:]:
                button.value = False

        # Keep track of which button is initially pressed.
        if switched_on:
            self._pressed_button = switched_on[0]

    def watch__selected(self) -> None:
        self.query(RadioButton).remove_class("-selected")
        if self._selected is not None:
            self._nodes[self._selected].add_class("-selected")
            self._scroll_to_selected()

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

    def _on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle a change to which button in the set is pressed.

        This handler ensures that, when a button is pressed, it's also the
        selected button.
        """
        self._selected = event.index

    async def _on_click(self, _: Click) -> None:
        """Handle a click on or within the radio set.

        This handler ensures that focus moves to the clicked radio set, even
        if there's a click on one of the radio buttons it contains.
        """
        self.focus()

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
        self._selected = _widget_navigation.find_next_enabled(
            self.children,
            anchor=self._selected,
            direction=-1,
        )

    def action_next_button(self) -> None:
        """Navigate to the next button in the set.

        Note that this will wrap around to the start if at the end.
        """
        self._selected = _widget_navigation.find_next_enabled(
            self.children,
            anchor=self._selected,
            direction=1,
        )

    def action_toggle_button(self) -> None:
        """Toggle the state of the currently-selected button."""
        if self._selected is not None:
            button = self._nodes[self._selected]
            assert isinstance(button, RadioButton)
            button.toggle()

    def _scroll_to_selected(self) -> None:
        """Ensure that the selected button is in view."""
        if self._selected is not None:
            button = self._nodes[self._selected]
            self.call_after_refresh(self.scroll_to_widget, button, animate=False)
