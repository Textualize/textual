from textual.app import App, ComposeResult
from textual.widgets import Button, Checkbox, Dialog, Input, Label


class DialogApp(App[None]):
    CSS_PATH = "dialog_complex.tcss"

    def compose(self) -> ComposeResult:
        with Dialog(title="Find and Replace"):
            yield Label("Find what:")
            yield Input(placeholder="The text to find")
            yield Label("Replace with:")
            yield Input(placeholder="The text to replace with")
            with Dialog.ActionArea():
                with Dialog.ActionArea.GroupLeft():
                    yield Checkbox("Regular Expression")
                yield Button("Cancel", variant="error")
                yield Button("First", variant="default")
                yield Button("All", variant="primary")


if __name__ == "__main__":
    DialogApp().run()
