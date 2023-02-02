from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Label, Static


class EditableText(Static):
    """Custom widget to show (editable) static text."""

    def compose(self) -> ComposeResult:
        yield Label()
        yield Input()
        yield Button()
        yield Button()


class EditableTextApp(App[None]):
    def compose(self) -> ComposeResult:
        yield EditableText()


app = EditableTextApp()


if __name__ == "__main__":
    app.run()
