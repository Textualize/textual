from textual.app import App
from textual.widgets import Label


class BorderApp(App):
    CSS_PATH = "border.tcss"

    def compose(self):
        yield Label("My border is solid red", id="label1")
        yield Label("My border is dashed green", id="label2")
        yield Label("My border is tall blue", id="label3")


if __name__ == "__main__":
    app = BorderApp()
    app.run()
