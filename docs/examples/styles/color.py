from textual.app import App
from textual.widgets import Label


class ColorApp(App):
    CSS_PATH = "color.tcss"

    def compose(self):
        yield Label("I'm red!", id="label1")
        yield Label("I'm rgb(0, 255, 0)!", id="label2")
        yield Label("I'm hsl(240, 100%, 50%)!", id="label3")


if __name__ == "__main__":
    app = ColorApp()
    app.run()
