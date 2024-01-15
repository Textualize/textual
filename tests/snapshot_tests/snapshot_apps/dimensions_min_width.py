"""
Regression test for https://github.com/Textualize/textual/issues/3721
and follow-up issues that were discovered.
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, TextArea, Label, Button, DataTable


class DimensionsApp(App[None]):
    CSS = """
    Horizontal {
        height: auto;
    }

    .ruler {
        text-style: reverse;
    }

    .target {
        width: 0;
        min-width: 50%;
        height: 3;
        border: solid red;
        box-sizing: border-box;
    }

    .padding {
        padding: 0 6;
    }

    .margin {
        margin: 0 10;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("1234567890" * 8, classes="ruler")
        with Horizontal():
            yield Label("1234567890" * 4, classes="target")
            yield Label("1234567890" * 4, classes="target")
        with Horizontal():
            yield Label("1234567890" * 4, classes="target padding")
            yield Label("1234567890" * 4, classes="target padding")
        yield Label("1234567890" * 8, classes="ruler")
        with Horizontal():
            yield Label("1234567890" * 4, classes="target margin")
            yield Label("1234567890" * 4, classes="target")
        with Horizontal():
            yield Label("1234567890" * 4, classes="target padding margin")
            yield Label("1234567890" * 4, classes="target padding")
        with Horizontal():
            yield Input(classes="target")
            yield Button(classes="target")
        with Horizontal():
            yield TextArea(classes="target")
            yield DataTable(classes="target")


if __name__ == "__main__":
    DimensionsApp().run()
