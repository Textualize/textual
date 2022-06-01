from textual.app import App
from textual.widgets import Button


class ButtonApp(App):
    CSS = """
    Button {
        width: 100%;
    }
    """

    def compose(self):
        yield Button("Light", id="light")
        yield Button("Dark", id="dark")

    def handle_pressed(self, event):
        self.dark = event.button.id == "dark"

