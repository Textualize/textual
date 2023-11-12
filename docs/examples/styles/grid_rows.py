from textual.app import App
from textual.containers import Grid
from textual.widgets import Label


class MyApp(App):
    CSS_PATH = "grid_rows.tcss"

    def compose(self):
        yield Grid(
            Label("1fr"),
            Label("1fr"),
            Label("height = 6"),
            Label("height = 6"),
            Label("25%"),
            Label("25%"),
            Label("1fr"),
            Label("1fr"),
            Label("height = 6"),
            Label("height = 6"),
        )


if __name__ == "__main__":
    app = MyApp()
    app.run()
