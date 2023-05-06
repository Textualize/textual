from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, cast

from rich.console import RenderableType
from rich.text import Text

from .. import events, on
from ..app import ComposeResult
from ..containers import Horizontal, Vertical
from ..message import Message
from ..reactive import var
from ..widget import Widget
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

    class Dismiss(Message):
        def __init__(self, lost_focus: bool = False) -> None:
            self.lost_focus = lost_focus
            super().__init__()

    class UpdateSelection(Message):
        def __init__(self, option_index: int) -> None:
            self.option_index = option_index
            super().__init__()

    def select(self, index: int | None) -> None:
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
    SelectCurrent Static#down-arrow {
        box-sizing: content-box;

        width: 1;
        height: 1;
        padding: 0 0 0 1;
        color: $text-muted;
        background: transparent;
    }
    """

    has_value = var(False)

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
        yield Static(self.placeholder, id="label")
        yield Static("▼", id="down-arrow")

    def _watch_has_value(self, has_value: bool) -> None:
        self.set_class(has_value, "-has-value")

    def _on_click(self) -> None:
        self.post_message(self.Toggle())


SelectOption: TypeAlias = tuple[str, object]

SelectType = TypeVar("SelectType")


class Select(Generic[SelectType], Widget, can_focus=True):
    BINDINGS = [("enter", "show_overlay")]
    DEFAULT_CSS = """
    Select {
        height: auto;
    }

    Select:focus SelectCurrent {
        border: tall $accent;
    }

    Select Vertical {
        height: auto;
    }

    SelectOverlay {
        width: 1fr;
        display: none;
        height: auto;
        max-height: 10;
        overlay: screen;
        constrain: y;
    }

    SelectOverlay.-show-overlay {
        display: block;
    }
    """

    show_overlay = var(False, init=False)
    prompt: var[str] = var[str]("Select")

    def __init__(
        self,
        *options: str | SelectOption,
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
            prompt: Text to show in the control when no option is select.
            allow_blank: Allow the selection of a blank option.
            value: Initial value.
            name: The name of the select control.
            id: The ID of the control the DOM.
            classes: The CSS classes of the control.
            disabled: Whether the control is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._options = [
            (option, option) if isinstance(option, str) else option
            for option in options
        ]
        if allow_blank:
            self._options.insert(0, ("", None))

        self.prompt = prompt
        self._select_options: list[Option] = [
            (
                Option(Text(self.prompt, style="dim"))
                if value is None
                else Option(prompt)
            )
            for prompt, value in self._options
        ]
        self._value = value

    @property
    def option_list(self) -> OptionList:
        """The option list."""
        option_list = self.query_one(SelectOverlay)
        return option_list

    @property
    def value(self) -> SelectType | None:
        return self._value

    @value.setter
    def value(self, value: SelectType | None) -> None:
        self._value = value
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
        with Vertical():
            yield SelectOverlay(*self._select_options)
            yield SelectCurrent(self.prompt)

    def on_mount(self) -> None:
        self.value = self._value

    def _watch_show_overlay(self, show_overlay: bool) -> None:
        overlay = self.query_one(SelectOverlay)
        if show_overlay:
            overlay.add_class("-show-overlay").focus()
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

        else:
            overlay.remove_class("-show-overlay")

    @on(SelectCurrent.Toggle)
    def select_current_toggle(self) -> None:
        self.show_overlay = not self.show_overlay

    @on(SelectOverlay.Dismiss)
    def select_overlay_dismiss(self, event: SelectOverlay.Dismiss) -> None:
        self.show_overlay = False
        if not event.lost_focus:
            self.focus()

    @on(SelectOverlay.UpdateSelection)
    def update_selection(self, event: SelectOverlay.UpdateSelection) -> None:
        value = cast("SelectType", self._options[event.option_index][1])
        self.value = value
        self.show_overlay = False
        self.focus()

    def action_show_overlay(self) -> None:
        select_current = self.query_one(SelectCurrent)
        select_current.has_value = True
        self.show_overlay = True


if __name__ == "__main__":
    from textual.app import App
    from textual.widgets import Input

    LINES = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain.""".splitlines()

    class SelectApp(App):
        CSS = """
        Screen {
            align: center middle;
        }

        Select {
            width: 30;
        }
        Input {
            width: 30;
        }

        """

        def compose(self) -> ComposeResult:
            yield Input(placeholder="Unrelated")
            yield Select(
                *(
                    *LINES,
                    "Paul",
                    "Leto",
                    "Alia",
                    "Chani",
                ),
                allow_blank=True,
            )
            yield Input(placeholder="Second unrelated")

    app = SelectApp()
    app.run()
