from __future__ import annotations

from typing import Generic, Iterable

from rich.console import RenderableType
from rich.text import Text

from textual import events, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import var
from textual.widgets import Input, OptionList
from textual.widgets._option_list import Option
from textual.widgets._select import SelectType


class ComboBoxInput(Input):
    """The input for the ComboBox control.

    Posts a bubbling message when it loses focus so the parent ComboBox
    can close the overlay.
    """

    class LostFocus(Message):
        """Posted when this input loses focus."""

    def _on_blur(self, event: events.Blur) -> None:
        super()._on_blur(event)
        self.post_message(self.LostFocus())


class ComboBoxOverlay(OptionList):
    """The 'pop-up' overlay for the ComboBox control."""

    ALLOW_SELECT = False


class ComboBox(Generic[SelectType], Vertical, can_focus=False):
    """Widget to search and select from a list of possible options.

    A ComboBox consists of an Input to search, and an overlaid OptionList
    to select from the filtered options.
    """

    BINDINGS = [
        Binding("down", "cursor_down", "Next option", show=False),
        Binding("up", "cursor_up", "Previous option", show=False),
        Binding("pagedown", "page_down", "Next page", show=False),
        Binding("pageup", "page_up", "Previous page", show=False),
        Binding("escape", "dismiss", "Dismiss menu", show=False),
    ]

    ALLOW_SELECT = False

    DEFAULT_CSS = """
    ComboBox {
        height: auto;
        color: $foreground;

        ComboBoxInput {
            width: 1fr;
        }

        & > ComboBoxOverlay {
            width: 1fr;
            display: none;
            height: auto;
            max-height: 12;
            overlay: screen;
            constrain: none inside;
            color: $foreground;
            border: tall $border-blurred;
            background: $surface;
            &:focus {
                background-tint: $foreground 5%;
            }
            & > .option-list--option {
                padding: 0 1;
            }
        }

        &.-expanded {
            & > ComboBoxOverlay {
                display: block;
            }
        }
    }
    """

    expanded: var[bool] = var(False, init=False)
    """True to show the overlay, otherwise False."""

    value: var[SelectType | None] = var(None, init=False)
    """The currently selected internal value. None if no selection is active."""

    class Selected(Message):
        """Posted when a selection has been made."""

        def __init__(self, combo_box: ComboBox[SelectType], value: SelectType | None) -> None:
            super().__init__()
            self.combo_box = combo_box
            self.value = value

        @property
        def control(self) -> ComboBox[SelectType]:
            return self.combo_box

    class Cleared(Message):
        """Posted when the selection has been cleared."""

        def __init__(self, combo_box: ComboBox[SelectType]) -> None:
            super().__init__()
            self.combo_box = combo_box

        @property
        def control(self) -> ComboBox[SelectType]:
            return self.combo_box

    def __init__(
        self,
        options: Iterable[tuple[RenderableType, SelectType]] | None = None,
        *,
        placeholder: str = "Search...",
        value: SelectType | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialize the ComboBox control.

        Args:
            options: Options to select from.
            placeholder: Text to show in the control when no option is selected.
            value: Initial value selected.
            name: The name of the control.
            id: The ID of the control in the DOM.
            classes: The CSS classes of the control.
            disabled: Whether the control is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.placeholder = placeholder
        self._initial_value = value

        # The authoritative list of all options
        self._options: list[tuple[RenderableType, SelectType]] = []
        if options is not None:
            self._options.extend(options)

    def compose(self) -> ComposeResult:
        """Compose the ComboBox with its Input and invisible Overlay."""
        yield ComboBoxInput(placeholder=self.placeholder, id="combo-box-input")
        yield ComboBoxOverlay()

    def _on_mount(self, _event: events.Mount) -> None:
        """Set initial values and options on mount."""
        if self._initial_value is not None:
            # Find the option and set the input
            for prompt, val in self._options:
                if val == self._initial_value:
                    input_widget = self.query_one(ComboBoxInput)
                    with input_widget.prevent(Input.Changed):
                        input_widget.value = self._get_plain_text(prompt)
                    self.value = self._initial_value
                    break

        self._update_overlay()

    def _watch_expanded(self, expanded: bool) -> None:
        """Update DOM visibility of overlay when expanded changes."""
        self.set_class(expanded, "-expanded")
        # Ensure our input still has focus if we are expanding.
        if expanded:
            try:
                overlay = self.query_one(ComboBoxOverlay)
                # Select the first option if nothing is highlighted
                if overlay.highlighted is None and overlay.option_count > 0:
                    overlay.highlighted = 0
            except NoMatches:
                pass

    @on(ComboBoxInput.LostFocus)
    def _input_blurred(self, event: ComboBoxInput.LostFocus) -> None:
        """Close the overlay when the input loses focus."""
        self.expanded = False

    @on(Input.Changed)
    def _input_changed(self, event: Input.Changed) -> None:
        """When input changes, filter the list and expand."""
        event.stop()
        self._update_overlay(event.value)
        
        try:
            overlay = self.query_one(ComboBoxOverlay)
        except NoMatches:
            return

        if overlay.option_count > 0:
            if not self.expanded:
                self.expanded = True
        else:
            self.expanded = False

    @on(ComboBoxOverlay.OptionSelected)
    def _option_selected(self, event: ComboBoxOverlay.OptionSelected) -> None:
        """Handle when a user clicks on an option."""
        event.stop()
        self._select_option(event.option_index)

    @on(Input.Submitted)
    def _input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter in the input.

        If the overlay is open and has a highlighted option, select it.
        Otherwise revert the input to the current selection (or clear it
        if nothing was ever selected).  This enforces strict predefined-
        option selection — free text that doesn't match an option is never
        accepted.
        """
        event.stop()
        try:
            overlay = self.query_one(ComboBoxOverlay)
        except NoMatches:
            return

        if self.expanded and overlay.highlighted is not None:
            self._select_option(overlay.highlighted)
        else:
            self._revert_input()

    def _get_plain_text(self, prompt: RenderableType) -> str:
        """Convert a RenderableType to plain text for matching and input setting."""
        if isinstance(prompt, str):
            return prompt
        elif isinstance(prompt, Text):
            return prompt.plain
        return str(prompt)

    def _update_overlay(self, search_query: str = "") -> None:
        """Update the options in the overlay based on the search query."""
        try:
            overlay = self.query_one(ComboBoxOverlay)
        except NoMatches:
            return

        overlay.clear_options()

        matching_options: list[Option] = []
        search_query = search_query.lower()

        # We keep track of which original Option matches which OptionList index
        # by passing the original index into the Option's id field.
        for index, (prompt, _) in enumerate(self._options):
            prompt_str = self._get_plain_text(prompt)
            if search_query in prompt_str.lower():
                matching_options.append(Option(prompt, id=str(index)))

        overlay.add_options(matching_options)
        if matching_options and overlay.highlighted is None:
            overlay.highlighted = 0

    def _select_option(self, overlay_index: int) -> None:
        """Select an option based on its index in the overlay."""
        try:
            overlay = self.query_one(ComboBoxOverlay)
            input_widget = self.query_one(ComboBoxInput)
        except NoMatches:
            return

        # Get the original index from the Option's ID
        option_id = overlay.get_option_at_index(overlay_index).id
        if option_id is None:
            return
            
        original_index = int(option_id)
        prompt, value = self._options[original_index]

        # Update state
        self.value = value
        
        # Pause emitting Changed before we modify the input to prevent recursive updates
        with input_widget.prevent(Input.Changed):
            input_widget.value = self._get_plain_text(prompt)

        self.expanded = False
        
        # Move cursor to end of input
        input_widget.cursor_position = len(input_widget.value)

        # Emit the selected message
        self.post_message(self.Selected(self, value))

    def _revert_input(self) -> None:
        """Revert the input text to match the current selection.

        If there is a selected value, restore its display text.
        If there is no selection, clear the input.
        """
        try:
            input_widget = self.query_one(ComboBoxInput)
        except NoMatches:
            return

        display_text = ""
        if self.value is not None:
            for prompt, val in self._options:
                if val == self.value:
                    display_text = self._get_plain_text(prompt)
                    break

        with input_widget.prevent(Input.Changed):
            input_widget.value = display_text
        input_widget.cursor_position = len(input_widget.value)
        self.expanded = False

    def action_cursor_down(self) -> None:
        """Proxy down key to overlay."""
        if not self.expanded:
            self.expanded = True
        else:
            try:
                self.query_one(ComboBoxOverlay).action_cursor_down()
            except NoMatches:
                pass

    def action_cursor_up(self) -> None:
        """Proxy up key to overlay."""
        try:
            self.query_one(ComboBoxOverlay).action_cursor_up()
        except NoMatches:
            pass

    def action_page_down(self) -> None:
        """Proxy page down to overlay."""
        if not self.expanded:
            self.expanded = True
        else:
            try:
                self.query_one(ComboBoxOverlay).action_page_down()
            except NoMatches:
                pass

    def action_page_up(self) -> None:
        """Proxy page up to overlay."""
        try:
            self.query_one(ComboBoxOverlay).action_page_up()
        except NoMatches:
            pass

    def action_dismiss(self) -> None:
        """Dismiss the overlay."""
        self.expanded = False
