from textual.app import App, ComposeResult
from textual.widgets import Log

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class LogApp(App):
    """An app with a simple log."""

    def compose(self) -> ComposeResult:
        yield Log()

    def on_ready(self) -> None:
        log = self.query_one(Log)
        log.write_line("Hello, World!")
        for _ in range(10):
            log.write_line(TEXT)


if __name__ == "__main__":
    app = LogApp()
    app.run()
