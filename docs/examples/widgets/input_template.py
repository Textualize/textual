from textual.app import App, ComposeResult
from textual.widgets import Input, Label


class InputApp(App):
    # (1)!
    CSS = """
    Input.-valid {
        border: tall $success 60%;
    }
    Input.-valid:focus {
        border: tall $success;
    }
    Input {
        margin: 1 1;
    }
    Label {
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Enter a valid credit card number.")
        yield Input(
            template="9999-9999-9999-9999",  # (2)!
        )


app = InputApp()

if __name__ == "__main__":
    app.run()
