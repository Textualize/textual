"""Provides a CheckboxSet widget, which groups checkboxes."""

from __future__ import annotations

from typing import ClassVar, Optional

import rich.repr

from ..binding import Binding, BindingType
from ..containers import Container
from ..events import Click, Mount
from ..message import Message
from ..reactive import var
from ._checkbox import Checkbox


class CheckboxSet(Container, can_focus=True, can_focus_children=False):
    """Widget for grouping a collection of checkboxes into a set.

    When a collection of [`Checkbox`][textual.widgets.Checkbox]es are
    grouped with this widget, they will be treated as a group with
    simplified navigation between the various checkboxes.
    """

    DEFAULT_CSS = """
    CheckboxSet {
        border: round #666;
        height: auto;
        width: auto;
    }

    CheckboxSet:focus {
        border: round $accent;
    }

    App.-light-mode CheckboxSet {
        border: round #CCC;
    }

    /* The following rules/styles mimic similar ToggleButton:focus rules in
     * ToggleButton. If those styles ever get updated, these should be too.
     */

    CheckboxSet:focus > Checkbox.-selected > .toggle--label {
        text-style: underline;
    }

    CheckboxSet:focus ToggleButton.-selected > .toggle--button {
        background: $foreground 25%;
    }

    CheckboxSet:focus > Checkbox.-on.-selected > .toggle--button {
        background: $foreground 25%;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("down,right", "next_button", "", show=False),
        Binding("enter,space", "toggle", "Toggle", show=False),
        Binding("up,left", "previous_button", "", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter, space | Toggle the currently-selected checkbox. |
    | left, up | Select the previous checkbox in the set. |
    | right, down | Select the next checkbox in the set. |
    """

    _selected: var[int | None] = var[Optional[int]](None)
    """The index of the currently-selected checkbox."""

    @rich.repr.auto
    class Changed(Message, bubble=True):
        """Posted when the state of a checkbox in the set changes.

        This message can be handled using an `on_checkbox_set_changed` method.
        """

        def __init__(self, checkbox_set: CheckboxSet, checkbox: Checkbox, value: bool) -> None:
            """Initialise the message.

            Args:
                checkbox: The checkbox that was pressed.
            """
            super().__init__()
            self.checkbox_set = checkbox_set
            """A reference to the [`CheckboxSet`][textual.widgets.CheckboxSet] that was changed."""
            self.checkbox = checkbox
            """A reference to the [`Checkbox`][textual.widgets.Checkbox] that changed value."""
            self.index = checkbox_set._nodes.index(checkbox)
            """The index of the [`Checkbox`][textual.widgets.Checkbox] that changed value."""
            self.value = value
            """The new value of the [`Checkbox`][textual.widgets.Checkbox]."""

        @property
        def control(self) -> CheckboxSet:
            """A reference to the [`CheckboxSet`][textual.widgets.CheckboxSet] that was changed.

            This is an alias for [`Changed.checkbox_set`][textual.widgets.CheckboxSet.Changed.checkbox_set]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.checkbox_set

        def __rich_repr__(self) -> rich.repr.Result:
            yield "checkbox_set", self.checkbox_set
            yield "checkbox", self.checkbox
            yield "index", self.index
            yield "value", self.value

    def __init__(
        self,
        *checkboxes: str | Checkbox,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the checkbox set.

        Args:
            checkboxes: A collection of labels or [`Checkbox`][textual.widgets.Checkbox]s to group together.
            name: The name of the checkbox set.
            id: The ID of the checkbox set in the DOM.
            classes: The CSS classes of the checkbox set.
            disabled: Whether the checkbox set is disabled or not.

        Note:
            When a `str` label is provided, a
            [Checkbox][textual.widgets.Checkbox] will be created from
            it.
        """
        self._checked_boxes: list[Checkbox] = []
        """Holds the checkboxes we're responsible for."""
        super().__init__(
            *[
                (checkbox if isinstance(checkbox, Checkbox) else Checkbox(checkbox))
                for checkbox in checkboxes
            ],
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def _on_mount(self, _: Mount) -> None:
        """Perform some processing once mounted in the DOM."""

        # If there are checkboxes, select the first one.
        if self._nodes:
            self._selected = 0

        # Get all the checkboxes within us
        checkboxes = list(self.query(Checkbox))

        # Checkboxes can have focus, by default. But we're going to take
        # that over and handle movement between them. So here we tell them
        # all they can't focus and also keep track of which checkboxes are
        # initially pressed.
        for checkbox in checkboxes:
            checkbox.can_focus = False
            if checkbox.value:
                self._checked_boxes.append(checkbox)

    def watch__selected(self) -> None:
        self.query(Checkbox).remove_class("-selected")
        if self._selected is not None:
            self._nodes[self._selected].add_class("-selected")
            self._nodes[self._selected].scroll_visible()

    def _on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Respond to the value of a checkbox in the set being changed.

        Args:
            event: The event.
        """
        # We're going to consume the underlying checkbox events, making
        # it appear as if they don't emit their own, as far as the caller is
        # concerned. As such, stop the event bubbling and also prohibit the
        # same event being sent out if/when we make a value change in here.
        event.stop()
        #with self.prevent(Checkbox.Changed):
        if event.checkbox.value and event.checkbox not in self._checked_boxes:
            self._checked_boxes.append(event.checkbox)
            self.post_message(self.Changed(self, event.checkbox, True))
        elif not event.checkbox.value and event.checkbox in self._checked_boxes:
            self._checked_boxes.remove(event.checkbox)
            self.post_message(self.Changed(self, event.checkbox, False))

    def _on_checkbox_set_changed(self, event: CheckboxSet.Changed) -> None:
        """Handle a change to which button in the set is pressed.

        This handler ensures that, when a button is pressed, it's also the
        selected button.
        """
        self._selected = event.index

    async def _on_click(self, _: Click) -> None:
        """Handle a click on or within the checkbox set.

        This handler ensures that focus moves to the clicked checkbox set, even
        if there's a click on one of the checkboxes it contains.
        """
        self.focus()

    @property
    def checked_boxes(self) -> list[Checkbox]:
        """The currently-checked [`Checkbox`][textual.widgets.Checkbox]es."""
        return self._checked_boxes

    @property
    def checked_index(self) -> list[int] | None:
        """The indexes of the currently-checked [`Checkbox`][textual.widgets.Checkbox]es."""
        r = []
        for checkbox in self._checked_boxes:
            r.append(self._nodes.index(checkbox))
        return r

    def action_previous_button(self) -> None:
        """Navigate to the previous checkbox in the set.

        Note that this will wrap around to the end if at the start.
        """
        if self._nodes:
            if self._selected == 0:
                self._selected = len(self.children) - 1
            elif self._selected is None:
                self._selected = 0
            else:
                self._selected -= 1

    def action_next_button(self) -> None:
        """Navigate to the next checkbox in the set.

        Note that this will wrap around to the start if at the end.
        """
        if self._nodes:
            if self._selected is None or self._selected == len(self._nodes) - 1:
                self._selected = 0
            else:
                self._selected += 1

    def action_toggle(self) -> None:
        """Toggle the state of the currently-selected checkbox."""
        if self._selected is not None:
            button = self._nodes[self._selected]
            assert isinstance(button, Checkbox)
            button.toggle()
