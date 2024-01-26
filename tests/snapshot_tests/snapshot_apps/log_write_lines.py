from textual.app import App, ComposeResult
from textual.widgets import Log
from textual.containers import Horizontal

TEXT = (
    """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain.
"""
    * 20
)


class LogApp(App):
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Log(id="log1", auto_scroll=False)
            yield Log(id="log2", auto_scroll=True)
            yield Log(id="log3")
            yield Log(id="log4", max_lines=6)

    def on_ready(self) -> None:
        self.query_one("#log1", Log).write_line(TEXT)
        self.query_one("#log2", Log).write_line(TEXT)
        self.query_one("#log3", Log).write_line(TEXT)
        self.query_one("#log4", Log).write_line(TEXT)

        self.query_one("#log3", Log).clear()
        self.query_one("#log3", Log).write_line("Hello, World")


if __name__ == "__main__":
    app = LogApp()
    app.run()
