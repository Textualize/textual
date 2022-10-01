from textual.app import App
from textual.widgets import Input


class InputApp(App):

    CSS = """
    Input {
       width: 20;
    }
    """

    def compose(self):
        yield Input("你123456789界", placeholder="Type something")


if __name__ == "__main__":
    app = InputApp()
    app.run()
