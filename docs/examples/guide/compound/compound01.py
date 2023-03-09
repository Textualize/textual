from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Input, Label


class InputWithLabel(Widget):
    """An input with a label."""

    DEFAULT_CSS = """
    InputWithLabel {
        layout: horizontal;
        height: auto;
    }
    InputWithLabel Label {
        padding: 1;
        width: 12;
        text-align: right;
    }
    InputWithLabel Input {
        width: 1fr;
    }
    """

    def __init__(self, input_label: str) -> None:
        self.input_label = input_label
        super().__init__()

    def compose(self) -> ComposeResult:  # (1)!
        yield Label(self.input_label)
        yield Input()


class CompoundApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    InputWithLabel {
        width: 80%;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield InputWithLabel("First Name")
        yield InputWithLabel("Last Name")
        yield InputWithLabel("Email")


if __name__ == "__main__":
    app = CompoundApp()
    app.run()
