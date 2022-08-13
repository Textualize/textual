from textual.app import App
from textual.widgets import Header, Footer


class FooterApp(App):
    def on_mount(self):
        self.sub_title = "Header and footer example"
        self.bind("b", "app.bell", description="Play the Bell")
        self.bind("d", "dark", description="Toggle dark")
        self.bind("f1", "app.bell", description="Hello World")

    def action_dark(self):
        self.dark = not self.dark

    def compose(self):
        yield Header()
        yield Footer()
