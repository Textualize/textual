from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from rich.console import RenderableType

from .. import events, on
from ..app import ComposeResult
from ..containers import Horizontal, Vertical
from ..message import Message
from ..reactive import var
from ..widget import Widget
from ..widgets import Static
from ._option_list import NewOptionListContent, Option, OptionList

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


class SelectOverlay(OptionList):
    """"""

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
        pass

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
        self.post_message(self.Dismiss())

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Inform parent when an option is selected."""
        self.post_message(self.UpdateSelection(event.option_index))


class SelectCurrent(Horizontal):
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
        height: 1;
        color: $text-disabled;
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
    }

    """

    has_value = var(False)

    class Toggle(Message):
        """Request toggle overlay."""

    def __init__(self, placeholder: str) -> None:
        super().__init__()
        self.placeholder = placeholder
        self.label: RenderableType | None = None

    def update(self, label: RenderableType | None) -> None:
        self.label = label
        self.has_value = label is not None
        self.query_one("#label", Static).update(
            self.placeholder if label is None else label
        )

    def compose(self) -> ComposeResult:
        yield Static(self.placeholder, id="label")
        yield Static("▼", id="down-arrow")

    def watch_has_value(self, has_value: bool) -> None:
        self.set_class(has_value, "-has-value")

    def on_click(self) -> None:
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
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._options = [
            (option, option) if isinstance(option, str) else option
            for option in options
        ]
        if allow_blank:
            self._options.insert(0, ("", None))

        self.prompt = prompt
        self._select_options: list[Option] = [
            Option(prompt) for prompt, _ in self._options
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
                for index, (prompt, prompt_value) in enumerate(self._options):
                    if value == prompt_value:
                        overlay.select(index)
                        break
                self.query_one(SelectCurrent).has_value = True

        else:
            overlay.remove_class("-show-overlay")
            self.focus()

    @on(SelectCurrent.Toggle)
    def select_current_toggle(self) -> None:
        self.show_overlay = not self.show_overlay

    @on(SelectOverlay.Dismiss)
    def select_overlay_dismiss(self) -> None:
        self.show_overlay = False

    @on(SelectOverlay.UpdateSelection)
    def update_selection(self, event: SelectOverlay.UpdateSelection) -> None:
        value = self._options[event.option_index][1]
        self.value = value

        # select_current.update(event.option.prompt)

        self.show_overlay = False

    def action_show_overlay(self) -> None:
        select_current = self.query_one(SelectCurrent)
        select_current.has_value = True
        self.show_overlay = True


if __name__ == "__main__":
    from textual.app import App
    from textual.widgets import Input

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
                *("Paul", "Jessica", "Leto", "Alia", "Chani"), allow_blank=False
            )
            yield Input(placeholder="Second unrelated")

    app = SelectApp()
    app.run()
