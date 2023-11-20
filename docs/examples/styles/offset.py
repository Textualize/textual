from textual.app import App
from textual.widgets import Label


class OffsetApp(App):
    CSS_PATH = "offset.tcss"

    def compose(self):
        yield Label("Paul (offset 8 2)", classes="paul")
        yield Label("Duncan (offset 4 10)", classes="duncan")
        yield Label("Chani (offset 0 -3)", classes="chani")


if __name__ == "__main__":
    app = OffsetApp()
    app.run()
