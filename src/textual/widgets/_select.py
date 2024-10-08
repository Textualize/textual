from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Iterable, TypeVar, Union

import rich.repr
from rich.console import RenderableType
from rich.text import Text

from textual import events, on
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import var
from textual.widgets import Static
from textual.widgets._option_list import Option, OptionList

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from textual.app import ComposeResult


class NoSelection:
    """Used by the `Select` widget to flag the unselected state. See [`Select.BLANK`][textual.widgets.Select.BLANK]."""

    def __repr__(self) -> str:
        return "Select.BLANK"


BLANK = NoSelection()


class InvalidSelectValueError(Exception):
    """Raised when setting a [`Select`][textual.widgets.Select] to an unknown option."""


class EmptySelectError(Exception):
    """Raised when a [`Select`][textual.widgets.Select] has no options and `allow_blank=False`."""


class SelectOverlay(OptionList):
    """The 'pop-up' overlay for the Select control."""

    BINDINGS = [("escape", "dismiss", "Dismiss menu")]

    DEFAULT_CSS = """
    SelectOverlay {
        border: tall $background;
        background: $panel;
        color: $text;
        width: 100%;
        padding: 0 1;
    }
    SelectOverlay:focus {
        border: tall $background;
    }
    SelectOverlay > .option-list--option {
        padding: 0 1;
    }
    """

    @dataclass
    class Dismiss(Message):
        """Inform ancestor the overlay should be dismissed."""

        lost_focus: bool = False
        """True if the overlay lost focus."""

    @dataclass
    class UpdateSelection(Message):
        """Inform ancestor the selection was changed."""

        option_index: int
        """The index of the new selection."""

    def select(self, index: int | None) -> None:
        """Move selection.

        Args:
            index: Index of new selection.
        """
        self.highlighted = index
        self.scroll_to_highlight(top=True)

    def action_dismiss(self) -> None:
        """Dismiss the overlay."""
        self.post_message(self.Dismiss())

    def _on_blur(self, _event: events.Blur) -> None:
        """On blur we want to dismiss the overlay."""
        self.post_message(self.Dismiss(lost_focus=True))
        self.suppress_click()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Inform parent when an option is selected."""
        event.stop()
        self.post_message(self.UpdateSelection(event.option_index))

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        """Stop option list highlighted messages leaking."""
        event.stop()


class SelectCurrent(Horizontal):
    """Displays the currently selected option."""

    DEFAULT_CSS = """
    SelectCurrent {
        border: tall transparent;
        background: $boost;
        color: $text;
        width: 100%;
        height: auto;
        padding: 0 2;

        Static#label {
            width: 1fr;
            height: auto;
            color: $text-disabled;
            background: transparent;
        }

        &.-has-value Static#label {
            color: $text;
        }

        .arrow {
            box-sizing: content-box;
            width: 1;
            height: 1;
            padding: 0 0 0 1;
            color: $text-muted;
            background: transparent;
        }
    }
    """

    has_value: var[bool] = var(False)
    """True if there is a current value, or False if it is None."""

    class Toggle(Message):
        """Request toggle overlay."""

    def __init__(self, placeholder: str) -> None:
        """Initialize the SelectCurrent.

        Args:
            placeholder: A string to display when there is nothing selected.
        """
        super().__init__()
        self.placeholder = placeholder
        self.label: RenderableType | NoSelection = Select.BLANK

    def update(self, label: RenderableType | NoSelection) -> None:
        """Update the content in the widget.

        Args:
            label: A renderable to display, or `None` for the placeholder.
        """
        self.label = label
        self.has_value = label is not Select.BLANK
        self.query_one("#label", Static).update(
            self.placeholder if isinstance(label, NoSelection) else label
        )

    def compose(self) -> ComposeResult:
        """Compose label and down arrow."""
        yield Static(self.placeholder, id="label")
        yield Static("▼", classes="arrow down-arrow")
        yield Static("▲", classes="arrow up-arrow")

    def _watch_has_value(self, has_value: bool) -> None:
        """Toggle the class."""
        self.set_class(has_value, "-has-value")

    async def _on_click(self, event: events.Click) -> None:
        """Inform ancestor we want to toggle."""
        event.stop()
        self.post_message(self.Toggle())


SelectType = TypeVar("SelectType")
"""The type used for data in the Select."""
SelectOption: TypeAlias = "tuple[str, SelectType]"
"""The type used for options in the Select."""


class Select(Generic[SelectType], Vertical, can_focus=True):
    """Widget to select from a list of possible options.

    A Select displays the current selection.
    When activated with ++enter++ the widget displays an overlay with a list of all possible options.
    """

    BLANK = BLANK
    """Constant to flag that the widget has no selection."""

    BINDINGS = [
        Binding("enter,down,space,up", "show_overlay", "Show menu", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter,down,space,up | Activate the overlay |
    """

    DEFAULT_CSS = """
    Select {
        height: auto;

        & > SelectOverlay {
            width: 1fr;
            display: none;
            height: auto;
            max-height: 12;
            overlay: screen;
            constrain: none inside;
        }

        &:focus > SelectCurrent {
            border: tall $accent;
        }

        .up-arrow {
            display: none;
        }

        &.-expanded .down-arrow {
            display: none;
        }

        &.-expanded .up-arrow {
            display: block;
        }

        &.-expanded > SelectOverlay {
            display: block;
        }

        &.-expanded > SelectCurrent {
            border: tall $accent;
        }
    }

    """

    expanded: var[bool] = var(False, init=False)
    """True to show the overlay, otherwise False."""
    prompt: var[str] = var[str]("Select")
    """The prompt to show when no value is selected."""
    value: var[SelectType | NoSelection] = var[Union[SelectType, NoSelection]](
        BLANK, init=False
    )
    """The value of the selection.

    If the widget has no selection, its value will be [`Select.BLANK`][textual.widgets.Select.BLANK].
    Setting this to an illegal value will raise a [`InvalidSelectValueError`][textual.widgets.select.InvalidSelectValueError]
    exception.
    """

    @rich.repr.auto
    class Changed(Message):
        """Posted when the select value was changed.

        This message can be handled using a `on_select_changed` method.
        """

        def __init__(
            self, select: Select[SelectType], value: SelectType | NoSelection
        ) -> None:
            """
            Initialize the Changed message.
            """
            super().__init__()
            self.select = select
            """The select widget."""
            self.value = value
            """The value of the Select when it changed."""

        def __rich_repr__(self) -> rich.repr.Result:
            yield self.select
            yield self.value

        @property
        def control(self) -> Select[SelectType]:
            """The Select that sent the message."""
            return self.select

    def __init__(
        self,
        options: Iterable[tuple[RenderableType, SelectType]],
        *,
        prompt: str = "Select",
        allow_blank: bool = True,
        value: SelectType | NoSelection = BLANK,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
    ):
        """Initialize the Select control.

        Args:
            options: Options to select from. If no options are provided then
                `allow_blank` must be set to `True`.
            prompt: Text to show in the control when no option is selected.
            allow_blank: Enables or disables the ability to have the widget in a state
                with no selection made, in which case its value is set to the constant
                [`Select.BLANK`][textual.widgets.Select.BLANK].
            value: Initial value selected. Should be one of the values in `options`.
                If no initial value is set and `allow_blank` is `False`, the widget
                will auto-select the first available option.
            name: The name of the select control.
            id: The ID of the control in the DOM.
            classes: The CSS classes of the control.
            disabled: Whether the control is disabled or not.
            tooltip: Optional tooltip.

        Raises:
            EmptySelectError: If no options are provided and `allow_blank` is `False`.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._allow_blank = allow_blank
        self.prompt = prompt
        self._value = value
        self._setup_variables_for_options(options)
        if tooltip is not None:
            self.tooltip = tooltip

    @classmethod
    def from_values(
        cls,
        values: Iterable[SelectType],
        *,
        prompt: str = "Select",
        allow_blank: bool = True,
        value: SelectType | NoSelection = BLANK,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> Select[SelectType]:
        """Initialize the Select control with values specified by an arbitrary iterable

        The options shown in the control are computed by calling the built-in `str`
        on each value.

        Args:
            values: Values used to generate options to select from.
            prompt: Text to show in the control when no option is selected.
            allow_blank: Enables or disables the ability to have the widget in a state
                with no selection made, in which case its value is set to the constant
                [`Select.BLANK`][textual.widgets.Select.BLANK].
            value: Initial value selected. Should be one of the values in `values`.
                If no initial value is set and `allow_blank` is `False`, the widget
                will auto-select the first available value.
            name: The name of the select control.
            id: The ID of the control in the DOM.
            classes: The CSS classes of the control.
            disabled: Whether the control is disabled or not.

        Returns:
            A new Select widget with the provided values as options.
        """
        options_iterator = [(str(value), value) for value in values]

        return cls(
            options_iterator,
            prompt=prompt,
            allow_blank=allow_blank,
            value=value,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def _setup_variables_for_options(
        self,
        options: Iterable[tuple[RenderableType, SelectType]],
    ) -> None:
        """Setup function for the auxiliary variables related to options.

        This method sets up `self._options` and `self._legal_values`.
        """
        self._options: list[tuple[RenderableType, SelectType | NoSelection]] = []
        if self._allow_blank:
            self._options.append(("", self.BLANK))
        self._options.extend(options)

        if not self._options:
            raise EmptySelectError(
                "Select options cannot be empty if selection can't be blank."
            )

        self._legal_values: set[SelectType | NoSelection] = {
            value for _, value in self._options
        }

    def _setup_options_renderables(self) -> None:
        """Sets up the `Option` renderables associated with the `Select` options."""
        self._select_options: list[Option] = [
            (
                Option(Text(self.prompt, style="dim"))
                if value == self.BLANK
                else Option(prompt)
            )
            for prompt, value in self._options
        ]

        option_list = self.query_one(SelectOverlay)
        option_list.clear_options()
        for option in self._select_options:
            option_list.add_option(option)

    def _init_selected_option(self, hint: SelectType | NoSelection = BLANK) -> None:
        """Initialises the selected option for the `Select`."""
        if hint == self.BLANK and not self._allow_blank:
            hint = self._options[0][1]
        self.value = hint

    def set_options(self, options: Iterable[tuple[RenderableType, SelectType]]) -> None:
        """Set the options for the Select.

        This will reset the selection. The selection will be empty, if allowed, otherwise
        the first valid option is picked.

        Args:
            options: An iterable of tuples containing the renderable to display for each
                option and the corresponding internal value.

        Raises:
            EmptySelectError: If the options iterable is empty and `allow_blank` is
                `False`.
        """
        self._setup_variables_for_options(options)
        self._setup_options_renderables()
        self._init_selected_option()

    def _validate_value(
        self, value: SelectType | NoSelection
    ) -> SelectType | NoSelection:
        """Ensure the new value is a valid option.

        If `allow_blank` is `True`, `None` is also a valid value and corresponds to no
            selection.

        Raises:
            InvalidSelectValueError: If the new value does not correspond to any known
                value.
        """
        if value not in self._legal_values:
            # It would make sense to use `None` to flag that the Select has no selection,
            # so we provide a helpful message to catch this mistake in case people didn't
            # realise we use a special value to flag "no selection".
            help_text = " Did you mean to use Select.clear()?" if value is None else ""
            raise InvalidSelectValueError(
                f"Illegal select value {value!r}." + help_text
            )

        return value

    def _watch_value(self, value: SelectType | NoSelection) -> None:
        """Update the current value when it changes."""
        self._value = value
        try:
            select_current = self.query_one(SelectCurrent)
        except NoMatches:
            pass
        else:
            if value == self.BLANK:
                select_current.update(self.BLANK)
            else:
                for index, (prompt, _value) in enumerate(self._options):
                    if _value == value:
                        select_overlay = self.query_one(SelectOverlay)
                        select_overlay.highlighted = index
                        select_current.update(prompt)
                        break
            self.post_message(self.Changed(self, value))

    def compose(self) -> ComposeResult:
        """Compose Select with overlay and current value."""
        yield SelectCurrent(self.prompt)
        yield SelectOverlay()

    def _on_mount(self, _event: events.Mount) -> None:
        """Set initial values."""
        self._setup_options_renderables()
        self._init_selected_option(self._value)

    def _watch_expanded(self, expanded: bool) -> None:
        """Display or hide overlay."""
        try:
            overlay = self.query_one(SelectOverlay)
        except NoMatches:
            # The widget has likely been removed
            return
        self.set_class(expanded, "-expanded")
        if expanded:
            overlay.focus()
            if self.value is self.BLANK:
                overlay.select(None)
                self.query_one(SelectCurrent).has_value = False
            else:
                value = self.value
                for index, (_prompt, prompt_value) in enumerate(self._options):
                    if value == prompt_value:
                        overlay.select(index)
                        break
                self.query_one(SelectCurrent).has_value = True

    @on(SelectCurrent.Toggle)
    def _select_current_toggle(self, event: SelectCurrent.Toggle) -> None:
        """Show the overlay when toggled."""
        event.stop()
        self.expanded = not self.expanded

    @on(SelectOverlay.Dismiss)
    def _select_overlay_dismiss(self, event: SelectOverlay.Dismiss) -> None:
        """Dismiss the overlay."""
        event.stop()
        self.expanded = False
        if not event.lost_focus:
            # If the overlay didn't lose focus, we want to re-focus the select.
            self.focus()

    @on(SelectOverlay.UpdateSelection)
    def _update_selection(self, event: SelectOverlay.UpdateSelection) -> None:
        """Update the current selection."""
        event.stop()
        value = self._options[event.option_index][1]
        if value != self.value:
            self.value = value

        async def update_focus() -> None:
            """Update focus and reset overlay."""
            self.focus()
            self.expanded = False

        self.call_after_refresh(update_focus)  # Prevents a little flicker

    def action_show_overlay(self) -> None:
        """Show the overlay."""
        select_current = self.query_one(SelectCurrent)
        select_current.has_value = True
        self.expanded = True
        # If we haven't opened the overlay yet, highlight the first option.
        select_overlay = self.query_one(SelectOverlay)
        if select_overlay.highlighted is None:
            select_overlay.action_first()

    def is_blank(self) -> bool:
        """Indicates whether this `Select` is blank or not.

        Returns:
            True if the selection is blank, False otherwise.
        """
        return self.value == self.BLANK

    def clear(self) -> None:
        """Clear the selection if `allow_blank` is `True`.

        Raises:
            InvalidSelectValueError: If `allow_blank` is set to `False`.
        """
        try:
            self.value = self.BLANK
        except InvalidSelectValueError:
            raise InvalidSelectValueError(
                "Can't clear selection if allow_blank is set to False."
            ) from None

    def _watch_prompt(self, prompt: str) -> None:
        if not self.is_mounted:
            return
        select_current = self.query_one(SelectCurrent)
        select_current.placeholder = prompt
        if not self._allow_blank:
            return
        if self.value == self.BLANK:
            select_current.update(self.BLANK)
        option_list = self.query_one(SelectOverlay)
        option_list.replace_option_prompt_at_index(0, Text(prompt, style="dim"))
