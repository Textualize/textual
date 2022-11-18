from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Placeholder


class PlaceholderApp(App):

    CSS_PATH = "placeholder.css"

    def compose(self) -> ComposeResult:
        yield Vertical(
            Container(
                Placeholder(label="This is a custom label for p1.", id="p1"),
                Placeholder(label="Placeholder p2 here!", id="p2"),
                Placeholder(id="p3"),
                Placeholder(id="p4"),
                Placeholder(id="p5"),
                Placeholder(),
                Horizontal(
                    Placeholder("size", id="col1"),
                    Placeholder("text", id="col2"),
                    Placeholder("size", id="col3"),
                    id="c1",
                ),
                id="bot"
            ),
            Container(
                Placeholder("text", id="left"),
                Placeholder("size", id="topright"),
                Placeholder("text", id="botright"),
                id="top",
            ),
            id="content",
        )


if __name__ == "__main__":
    app = PlaceholderApp()
    app.run()
