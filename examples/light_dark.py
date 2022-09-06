from textual.app import App
from textual.widgets import Button


class ButtonApp(App):

    DEFAULT_CSS = """
    Button {
        width: 100%;
    }
    """

    def compose(self):
        yield Button("Lights off")

    def on_button_pressed(self, event):
        self.dark = not self.dark
        self.bell()
        event.button.label = "Lights ON" if self.dark else "Lights OFF"
