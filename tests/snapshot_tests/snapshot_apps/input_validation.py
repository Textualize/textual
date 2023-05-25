from textual.app import App, ComposeResult
from textual.validation import Number
from textual.widgets import Input

VALIDATORS = [
    Number(minimum=1, maximum=5),
]


class InputApp(App):
    CSS = """
    Input.-valid {
        border: tall $success 60%;
    }
    Input.-valid:focus {
        border: tall $success;
    }
    Input {
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Enter a number between 1 and 5",
            validators=VALIDATORS,
        )
        yield Input(
            placeholder="Enter a number between 1 and 5",
            validators=VALIDATORS,
        )
        yield Input(
            placeholder="Enter a number between 1 and 5",
            validators=VALIDATORS,
        )
        yield Input(
            placeholder="Enter a number between 1 and 5",
            validators=VALIDATORS,
        )


app = InputApp()

if __name__ == '__main__':
    app.run()
