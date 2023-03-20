from textual.app import App
from textual.containers import Grid
from textual.widgets import Label


class ProgrammaticScrollbarGutterChange(App[None]):
    CSS = """
    Grid { grid-size: 2 2; scrollbar-size: 5 5; }
    Label { width: 100%; height: 100%; background: red; }
    """

    def compose(self):
        yield Grid(
            Label("one"),
            Label("two"),
            Label("three"),
            Label("four"),
        )

    def on_key(self, event):
        if event.key == "s":
            self.query_one(Grid).styles.scrollbar_gutter = "stable"


if __name__ == "__main__":
    app = ProgrammaticScrollbarGutterChange()
    app.run()
