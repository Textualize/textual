from textual.app import App, ComposeResult
from textual.restriction import Restrictor
from textual.widgets import Input, Label, Pretty


class InputApp(App):
    # (6)!
    CSS = """
    Input {
        margin: 1 1;
    }
    Label {
        margin: 1 2;
    }
    Pretty {
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Enter uppercase text")
        yield Input(
            placeholder="Enter uppercase text...",
            restrictors=[UppercaseRestrictor()],
        )
        yield Pretty([])


# A custom restrictor
class UppercaseRestrictor(Restrictor):
    def allowed(self, value: str) -> bool:
        return value.isupper()


app = InputApp()

if __name__ == "__main__":
    app.run()
