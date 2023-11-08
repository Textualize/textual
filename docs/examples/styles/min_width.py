from textual.app import App
from textual.containers import VerticalScroll
from textual.widgets import Placeholder


class MinWidthApp(App):
    CSS_PATH = "min_width.tcss"

    def compose(self):
        yield VerticalScroll(
            Placeholder("min-width: 25%", id="p1"),
            Placeholder("min-width: 75%", id="p2"),
            Placeholder("min-width: 100", id="p3"),
            Placeholder("min-width: 400h", id="p4"),
        )


if __name__ == "__main__":
    app = MinWidthApp()
    app.run()
