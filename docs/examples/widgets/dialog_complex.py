from textual.app import App, ComposeResult
from textual.widgets import Button, Checkbox, Dialog, Input, Label


class DialogApp(App[None]):
    CSS_PATH = "dialog_complex.tcss"

    def compose(self) -> ComposeResult:
        with Dialog(title="Find and replace"):
            yield Label("Find what:")  # (1)!
            yield Input(placeholder="The text to find")  # (2)!
            yield Label("Replace with:")  # (3)!
            yield Input(placeholder="The text to replace with")  # (4)!
            with Dialog.ActionArea():  # (5)!
                with Dialog.ActionArea.GroupLeft():  # (6)!
                    yield Checkbox("Ignore case")  # (7)!
                yield Button("Cancel", variant="error")  # (8)!
                yield Button("First", variant="default")  # (9)!
                yield Button("All", variant="primary")  # (10)!


if __name__ == "__main__":
    DialogApp().run()
