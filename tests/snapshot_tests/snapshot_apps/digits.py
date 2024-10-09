from textual.app import App, ComposeResult
from textual.widgets import Digits


class DigitApp(App):
    CSS = """
    .left {
        text-align: left;
    }
    .center {
        text-align:center;
    }
    .right {
        text-align:right;
    }
    .bold {
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        yield Digits("3.1427", classes="left")
        yield Digits(" 0123456789+-.,ABCDEF", classes="center")
        yield Digits(" 0123456789+-.,ABCDEF", classes="center bold")
        yield Digits("3x10^4", classes="right")


if __name__ == "__main__":
    app = DigitApp()
    app.run()
