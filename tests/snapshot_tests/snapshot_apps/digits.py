from textual.app import App, ComposeResult
from textual.widgets import Digits


class DigitApp(App):
    CSS = """
    #digits1 {
        text-align: left;
    }
    #digits2 {
        text-align:center;
    }
    #digits3 {
        text-align:right;
    }
    """

    def compose(self) -> ComposeResult:
        yield Digits("3.1427", id="digits1")
        yield Digits(" 0123456789+-.,", id="digits2")
        yield Digits("3x10^4", id="digits3")


if __name__ == "__main__":
    app = DigitApp()
    app.run()
