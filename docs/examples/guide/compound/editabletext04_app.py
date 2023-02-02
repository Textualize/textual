from textual.app import App, ComposeResult
from textual.widgets import Label

from editabletext04 import EditableText


class EditableText04App(App[None]):
    def compose(self) -> ComposeResult:
        yield Label("First name")
        yield EditableText()
        yield Label("Last name")
        yield EditableText()
        yield Label("Preferred name")
        yield EditableText()

    def on_mount(self) -> None:
        for editable_text in self.query(EditableText):
            editable_text.switch_to_editing_mode()  # (1)!


app = EditableText04App()


if __name__ == "__main__":
    app.run()
