from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Iterable, Optional, TypeVar

from rich.console import RenderableType
from rich.text import Text

from .. import events, on
from ..app import ComposeResult
from ..containers import Horizontal, Vertical
from ..css.query import NoMatches
from ..message import Message
from ..reactive import var
from ..widgets import Static
from ._option_list import Option, OptionList

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


class SelectOverlay(OptionList):
    """The 'pop-up' overlay for the Select control."""

    BINDINGS = [("escape", "dismiss")]

    DEFAULT_CSS = """
    SelectOverlay {
        border: tall $background;
        background: $panel;
        color: $text;
        width: 100%;
        padding: 0 1;
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

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Inform parent when an option is selected."""
        event.stop()
        self.post_message(self.UpdateSelection(event.option_index))


class SelectCurrent(Horizontal):
    """Displays the currently selected option."""

    DEFAULT_CSS = """
    SelectCurrent {
        border: tall $background;
        background: $boost;
        color: $text;
        width: 100%;
        height: auto;
        padding: 0 2;
    }
    SelectCurrent Static#label {
        width: 1fr;
        height: auto;
        color: $text-disabled;
        background: transparent;
    }
    SelectCurrent.-has-value Static#label {
        color: $text;
    }
    SelectCurrent .arrow {
        box-sizing: content-box;
        width: 1;
        height: 1;
        padding: 0 0 0 1;
        color: $text-muted;
        background: transparent;
    }
    SelectCurrent .arrow {
        box-sizing: content-box;
        width: 1;
        height: 1;
        padding: 0 0 0 1;
        color: $text-muted;
        background: transparent;
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
        self.label: RenderableType | None = None

    def update(self, label: RenderableType | None) -> None:
        """Update the content in the widget.

        Args:
            label: A renderable to display, or `None` for the placeholder.
        """
        self.label = label
        self.has_value = label is not None
        self.query_one("#label", Static).update(
            self.placeholder if label is None else label
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

    BINDINGS = [("enter,down,space,up", "show_overlay")]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter,down,space,up | Activate the overlay |
    """

    DEFAULT_CSS = """
    Select {
        height: auto;
    }

    Select:focus > SelectCurrent {
        border: tall $accent;
    }

    Select > SelectOverlay {
        width: 1fr;
        display: none;
        height: auto;
        max-height: 10;
        overlay: screen;
        constrain: y;
    }

    Select .up-arrow {
        display:none;
    }

    Select.-expanded .down-arrow {
        display:none;
    }

    Select.-expanded .up-arrow {
        display: block;
    }

    Select.-expanded > SelectOverlay {
        display: block;
    }

    Select.-expanded > SelectCurrent {
        border: tall $accent;
    }
    """

    expanded: var[bool] = var(False, init=False)
    """True to show the overlay, otherwise False."""
    prompt: var[str] = var[str]("Select")
    """The prompt to show when no value is selected."""
    value: var[SelectType | None] = var[Optional[SelectType]](None)
    """The value of the select."""

    class Changed(Message, bubble=True):
        """Posted when the select value was changed.

        This message can be handled using a `on_select_changed` method.

        """

        def __init__(self, control: Select, value: SelectType | None) -> None:
            """
            Initialize the Changed message.

            """
            super().__init__()
            self.control = control
            """The select control."""
            self.value = value
            """The value of the Select when it changed."""

    def __init__(
        self,
        options: Iterable[tuple[str, SelectType]],
        *,
        prompt: str = "Select",
        allow_blank: bool = True,
        value: SelectType | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialize the Select control

        Args:
            options: Options to select from.
            prompt: Text to show in the control when no option is select.
            allow_blank: Allow the selection of a blank option.
            value: Initial value (should be one of the values in `options`).
            name: The name of the select control.
            id: The ID of the control the DOM.
            classes: The CSS classes of the control.
            disabled: Whether the control is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._allow_blank = allow_blank
        self.prompt = prompt
        self._initial_options = list(options)
        self._value: SelectType | None = value

    def set_options(self, options: Iterable[tuple[RenderableType, SelectType]]) -> None:
        """Set the options for the Select.

        Args:
            options: An iterable of tuples containing (STRING, VALUE).
        """
        self._options: list[tuple[RenderableType, SelectType | None]] = list(options)

        if self._allow_blank:
            self._options.insert(0, ("", None))

        self._select_options: list[Option] = [
            (
                Option(Text(self.prompt, style="dim"))
                if value is None
                else Option(prompt)
            )
            for prompt, value in self._options
        ]

        option_list = self.query_one(SelectOverlay)
        option_list.clear_options()
        for option in self._select_options:
            option_list.add_option(option)

    def _watch_value(self, value: SelectType | None) -> None:
        """Update the current value when it changes."""
        self._value = value
        try:
            select_current = self.query_one(SelectCurrent)
        except NoMatches:
            pass
        else:
            if value is None:
                self.query_one(SelectCurrent).update(None)
            else:
                for index, (prompt, _value) in enumerate(self._options):
                    if _value == value:
                        select_overlay = self.query_one(SelectOverlay)
                        select_overlay.highlighted = index
                        self.query_one(SelectCurrent).update(prompt)
                        break
                else:
                    self.query_one(SelectCurrent).update(None)

    def compose(self) -> ComposeResult:
        """Compose Select with overlay and current value."""
        yield SelectCurrent(self.prompt)
        yield SelectOverlay()

    def _on_mount(self, _event: events.Mount) -> None:
        """Set initial values."""
        self.set_options(self._initial_options)
        self.value = self._value

    def _watch_expanded(self, expanded: bool) -> None:
        """Display or hide overlay."""
        overlay = self.query_one(SelectOverlay)
        self.set_class(expanded, "-expanded")
        if expanded:
            overlay.focus()
            if self.value is None:
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
        self.value = value

        async def update_focus() -> None:
            """Update focus and reset overlay."""
            self.focus()
            self.expanded = False

        self.call_after_refresh(update_focus)  # Prevents a little flicker
        self.post_message(self.Changed(self, value))

    def action_show_overlay(self) -> None:
        """Show the overlay."""
        select_current = self.query_one(SelectCurrent)
        select_current.has_value = True
        self.expanded = True
