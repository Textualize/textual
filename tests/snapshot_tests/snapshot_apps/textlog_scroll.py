from textual.app import App, ComposeResult
from textual.widgets import TextLog
from textual.containers import Horizontal


class TextLogScrollApp(App):
    CSS = """
    TextLog{
        width: 1fr;
        height: 10;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            # Don't scroll on write
            yield TextLog(id="textlog1", auto_scroll=False)
            # Scroll on write
            yield TextLog(id="textlog2", auto_scroll=True)
            # Scroll on write, but disabled on write()
            yield TextLog(id="textlog3", auto_scroll=True)

    def on_ready(self) -> None:
        lines = [f"Line {n}" for n in range(20)]
        for line in lines:
            self.query_one("#textlog1", TextLog).write(line)
        for line in lines:
            self.query_one("#textlog2", TextLog).write(line)
        for line in lines:
            self.query_one("#textlog3", TextLog).write(line, scroll_end=False)


if __name__ == "__main__":
    app = TextLogScrollApp()
    app.run()
