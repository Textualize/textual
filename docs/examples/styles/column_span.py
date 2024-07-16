from textual.app import App
from textual.containers import Grid
from textual.widgets import Placeholder


class MyApp(App):
    CSS_PATH = "column_span.tcss"

    def compose(self):
        yield Grid(
            Placeholder(id="p1"),
            Placeholder(id="p2"),
            Placeholder(id="p3"),
            Placeholder(id="p4"),
            Placeholder(id="p5"),
            Placeholder(id="p6"),
            Placeholder(id="p7"),
        )


if __name__ == "__main__":
    app = MyApp()
    app.run()
