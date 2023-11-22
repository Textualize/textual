from textual.app import App
from textual.containers import Grid
from textual.widgets import Label


class MyApp(App):
    CSS_PATH = "grid_size_columns.tcss"

    def compose(self):
        yield Grid(
            Label("1"),
            Label("2"),
            Label("3"),
            Label("4"),
            Label("5"),
        )


if __name__ == "__main__":
    app = MyApp()
    app.run()
