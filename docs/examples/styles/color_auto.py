from textual.app import App
from textual.widgets import Label


class ColorApp(App):
    CSS_PATH = "color_auto.tcss"

    def compose(self):
        yield Label("The quick brown fox jumps over the lazy dog!", id="lbl1")
        yield Label("The quick brown fox jumps over the lazy dog!", id="lbl2")
        yield Label("The quick brown fox jumps over the lazy dog!", id="lbl3")
        yield Label("The quick brown fox jumps over the lazy dog!", id="lbl4")
        yield Label("The quick brown fox jumps over the lazy dog!", id="lbl5")


if __name__ == "__main__":
    app = ColorApp()
    app.run()
