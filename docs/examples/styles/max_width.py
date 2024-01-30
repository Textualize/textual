from textual.app import App
from textual.containers import VerticalScroll
from textual.widgets import Placeholder


class MaxWidthApp(App):
    CSS_PATH = "max_width.tcss"

    def compose(self):
        yield VerticalScroll(
            Placeholder("max-width: 50h", id="p1"),
            Placeholder("max-width: 999", id="p2"),
            Placeholder("max-width: 50%", id="p3"),
            Placeholder("max-width: 30", id="p4"),
        )


if __name__ == "__main__":
    app = MaxWidthApp()
    app.run()
