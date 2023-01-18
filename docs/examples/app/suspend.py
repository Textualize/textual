import subprocess
import sys

from textual.app import App, ComposeResult
from textual.widgets import Footer, Static


class SuspendApp(App):
    BINDINGS = [
        ("r", "open_repl", "Open REPL"),
    ]

    def compose(self) -> ComposeResult:
        yield Static(
            "Press r to open the Python built-in REPL. Run quit() to return to the app."
        )
        yield Footer()

    def action_open_repl(self) -> None:
        with self.suspend():
            subprocess.run(sys.executable)


if __name__ == "__main__":
    app = SuspendApp()
    app.run()
