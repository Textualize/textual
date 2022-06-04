from textual.app import App
from textual.widgets import Button


class ButtonApp(App):

    CSS = """

    Button {
        width: 100%;
    }

    """

    def compose(self):
        yield Button("Lights off")

    def handle_pressed(self, event):
        self.dark = not self.dark
        event.button.label = "Lights ON" if self.dark else "Lights OFF"
