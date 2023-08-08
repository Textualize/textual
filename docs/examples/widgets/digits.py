from textual.app import App, ComposeResult
from textual.widgets import Digits


class DigitApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    #pi {
        border: double green;
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Digits("3.141,592,653,5897", id="pi")


app = DigitApp()
app.run()
