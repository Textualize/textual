"""
Regression test for https://github.com/Textualize/textual/issues/3721
and follow-up issues that were discovered.
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, TextArea, Label, Button, DataTable


class DimensionsApp(App[None]):
    CSS = """
    Vertical {
        width: auto;
    }

    .ruler {
        text-style: reverse;
        height: 24;
        width: 1;
    }

    .target {
        width: 3;
        height: 0;
        min-height: 50%;
        border: solid red;
        box-sizing: border-box;
    }

    Input.target, Button.target, TextArea.target, DataTable.target {
        width: 12;
        min-width: 0;  # "Unset" Button's min-width.
    }

    .padding {
        padding: 1 0;
    }

    .margin {
        margin: 2 0;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label("1234567890" * 3, classes="ruler")
            with Vertical():
                yield Label("123456789012", classes="target")
                yield Label("123456789012", classes="target")
            with Vertical():
                yield Label("123456789012", classes="target padding")
                yield Label("123456789012", classes="target padding")
            yield Label("1234567890" * 3, classes="ruler")
            with Vertical():
                yield Label("123456789012", classes="target margin")
                yield Label("123456789012", classes="target")
            with Vertical():
                yield Label("123456789012", classes="target padding margin")
                yield Label("123456789012", classes="target padding")
            yield Label("1234567890" * 3, classes="ruler")
            with Vertical():
                yield Input(classes="target")
                yield Button(classes="target")
            with Vertical():
                yield TextArea(classes="target")
                yield DataTable(classes="target")

    def on_mount(self) -> None:
        self.query_one(Input).cursor_blink = False
        self.query_one(TextArea).cursor_blink = False


if __name__ == "__main__":
    DimensionsApp().run()
