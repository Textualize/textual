from __future__ import annotations

from rich.text import Text, TextType

from .. import on
from ..app import ComposeResult
from ..binding import Binding
from ..containers import Horizontal, Vertical
from ..message import Message
from ..reactive import var
from ..widget import Widget
from ..widgets import Static
from ._option_list import NewOptionListContent, OptionList


class SelectOverlay(OptionList):
    BINDINGS = [("escape", "dismiss")]

    DEFAULT_CSS = """
    SelectOverlay {
        border: tall $background;
        background: $boost;
        color: $text;
        width: 100%;
        padding: 0 0;
    }
    SelectOverlay > .option-list--option {
        padding: 0 1;
    }
    """

    class Dismiss(Message):
        pass

    def action_dismiss(self) -> None:
        self.post_message(self.Dismiss())

    def on_blur(self) -> None:
        self.post_message(self.Dismiss())


class SelectCurrent(Static):
    DEFAULT_CSS = """

    SelectCurrent {
        border: tall $background;
        background: $boost;
        color: $text;
        width: 100%;
        padding: 0 1;
    }


    SelectCurrent Static#label {
        width: 1fr;
        height: 1;
        color: $text-muted;
    }
    SelectCurrent.-has-value Static#label {
        color: $text;
    }

    SelectCurrent Static#down-arrow {
        box-sizing: content-box;

        width: 1;
        height: 1;
        padding: 0 1;
    }

    """

    has_value = var(False)

    class Toggle(Message):
        """Request toggle overlay."""

    def __init__(self, label: Text) -> None:
        super().__init__()
        self.label = label

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static(self.label, id="label")
            yield Static(Text("▼"), id="down-arrow")

    def watch_has_value(self, has_value: bool) -> None:
        self.set_class(has_value, "-has-value")

    def on_click(self) -> None:
        self.post_message(self.Toggle())


class Select(Widget, can_focus=True):
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
        height: 10;
        flow: overlay;
    }

    SelectOverlay.-show-overlay {
        display: block;
    }
    """

    show_overlay = var(False, init=False)
    prompt: var[str] = var[str]("Select")

    def __init__(
        self,
        *content: NewOptionListContent,
        prompt: str = "Select",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.content = content
        self.prompt = prompt

    def compose(self) -> ComposeResult:
        with Vertical():
            yield SelectOverlay(*self.content)
            yield SelectCurrent(Text("Click Me"))

    async def _watch_prompt(self, prompt: str | None) -> None:
        self.query_one(SelectCurrent).update("Select" if prompt is None else prompt)

    def _watch_show_overlay(self, show_overlay: bool) -> None:
        overlay = self.query_one(SelectOverlay)
        if show_overlay:
            overlay.add_class("-show-overlay").focus()
        else:
            overlay.remove_class("-show-overlay")
            self.focus()

    @on(SelectCurrent.Toggle)
    def select_current_toggle(self) -> None:
        self.show_overlay = not self.show_overlay

    @on(SelectOverlay.Dismiss)
    def select_overlay_dismiss(self) -> None:
        self.show_overlay = False

    def action_show_overlay(self) -> None:
        self.show_overlay = True


if __name__ == "__main__":
    from textual.app import App

    class SelectApp(App):
        CSS = """
        Screen {
            align: center middle;
        }

        Select {
            width: 30;
        }

        """

        def compose(self) -> ComposeResult:
            yield Select("Hello", "World")

    app = SelectApp()
    app.run()
