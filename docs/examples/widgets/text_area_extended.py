from textual import events
from textual.app import App, ComposeResult
from textual.widgets import TextArea


class ExtendedTextArea(TextArea):
    """A subclass of TextArea with parenthesis-closing functionality."""

    def __init__(
        self,
        text: str = "",
        *,
        language: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False
    ) -> None:
        super().__init__(
            text=text,
            language=language,
            theme="monokai",
            soft_wrap=False,
            tab_behaviour="indent",
            show_line_numbers=True,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def _on_key(self, event: events.Key) -> None:
        if event.character == "(":
            self.insert("()")
            self.move_cursor_relative(columns=-1)
            event.prevent_default()


class TextAreaKeyPressHook(App):
    def compose(self) -> ComposeResult:
        yield ExtendedTextArea(language="python")


app = TextAreaKeyPressHook()
if __name__ == "__main__":
    app.run()
