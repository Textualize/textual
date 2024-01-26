from textual.app import App
from textual.widgets import Label


class AlignApp(App):
    CSS_PATH = "align.tcss"

    def compose(self):
        yield Label("Vertical alignment with [b]Textual[/]", classes="box")
        yield Label("Take note, browsers.", classes="box")


if __name__ == "__main__":
    app = AlignApp()
    app.run()
