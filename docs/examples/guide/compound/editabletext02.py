from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Label, Static


class EditableText(Static):
    """Custom widget to show (editable) static text."""

    DEFAULT_CSS = ""  # default styling should go here.  # (1)!

    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Type something...", classes="editabletext--input ethidden"
        )
        yield Label("", classes="editabletext--label")
        yield Button("📝", classes="editabletext--edit")
        yield Button("✅", classes="editabletext--confirm")


class EditableTextApp(App[None]):
    def compose(self) -> ComposeResult:
        yield EditableText()


app = EditableTextApp(css_path="editabletext_defaultcss.css")  # (2)!


if __name__ == "__main__":
    app.run()
