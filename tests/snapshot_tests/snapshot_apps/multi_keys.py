from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer

class MApp(App):
    BINDINGS = [Binding("o,ctrl+o", "options", "Options")]
    def compose(self) -> ComposeResult:
        yield Footer()

if __name__ == "__main__":
    MApp().run()
