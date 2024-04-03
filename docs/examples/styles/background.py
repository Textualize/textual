from textual.app import App
from textual.widgets import Label


class BackgroundApp(App):
    CSS_PATH = "background.tcss"

    def compose(self):
        yield Label("Widget 1", id="static1")
        yield Label("Widget 2", id="static2")
        yield Label("Widget 3", id="static3")


if __name__ == "__main__":
    app = BackgroundApp()
    app.run()
