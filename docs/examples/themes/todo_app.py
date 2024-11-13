from itertools import cycle

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, Label, SelectionList


class TodoList(App[None]):
    CSS = """
Screen {
    align: center middle;
    hatch: right $foreground 10%;
}
#content {
    height: auto;
    width: 40;
    padding: 1 2;
}
#header {
    height: 1;
    width: auto;
    margin-bottom: 1;
}
.title {
    text-style: bold;
    padding: 0 1;
    width: 1fr;
}
#overdue {
    color: $text-error;
    background: $error-muted;
    padding: 0 1;
    width: auto;
}
#done {
    color: $text-success;
    background: $success-muted;
    padding: 0 1;
    margin: 0 1;
}
#footer {
    height: auto;
    margin-bottom: 2;
}
#history-header {
    height: 1;
    width: auto;
}
#history-done {
    width: auto;
    padding: 0 1;
    margin: 0 1;
    background: $primary-muted;
    color: $text-primary;
}
"""

    BINDINGS = [Binding("ctrl+t", "cycle_theme", "Cycle theme")]
    THEMES = cycle(
        ["nord", "gruvbox", "tokyo-night", "textual-dark", "solarized-light"]
    )

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="content"):
            with Horizontal(id="header"):
                yield Label("Today", classes="title")
                yield Label("1 overdue", id="overdue")
                yield Label("1 done", id="done")
            yield SelectionList(
                ("Buy milk", 0),
                ("Buy bread", 1),
                ("Go and vote", 2, True),
                ("Return package", 3),
                id="todo-list",
            )
            with Horizontal(id="footer"):
                yield Input(placeholder="Add a task")

            with Horizontal(id="history-header"):
                yield Label("History", classes="title")
                yield Label("4 items", id="history-done")

        yield Footer()

    def on_mount(self) -> None:
        self.action_cycle_theme()

    def action_cycle_theme(self) -> None:
        self.theme = next(self.THEMES)


app = TodoList()
if __name__ == "__main__":
    app.run()
