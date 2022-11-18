from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer


class KeyDisplayApp(App):
    """Tests how keys are displayed in the Footer, and ensures
    that overriding the key_displays works as expected.
    Exercises both the built-in Textual key display replacements,
    and user supplied replacements.
    Will break when we update the Footer - but we should add a similar
    test (or updated snapshot) for the updated Footer."""
    BINDINGS = [
        Binding("question_mark", "question", "Question"),
        Binding("ctrl+q", "quit", "Quit app"),
        Binding("escape", "escape", "Escape"),
        Binding("a", "a", "Letter A"),
    ]

    def compose(self) -> ComposeResult:
        yield Footer()

    def get_key_display(self, key: str) -> str:
        key_display_replacements = {
            "escape": "Escape!",
            "ctrl+q": "^q",
        }
        display = key_display_replacements.get(key)
        if display:
            return display
        return super().get_key_display(key)


app = KeyDisplayApp()
if __name__ == '__main__':
    app.run()
