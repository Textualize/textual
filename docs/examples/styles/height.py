from textual.app import App
from textual.widget import Widget


class HeightApp(App):
    CSS_PATH = "height.tcss"

    def compose(self):
        yield Widget()


if __name__ == "__main__":
    app = HeightApp()
    app.run()
