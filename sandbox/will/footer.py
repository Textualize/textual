from textual.app import App
from textual.widgets import Footer


class FooterApp(App):
    def on_mount(self):
        self.dark = True
        self.bind("b", "app.bell", description="Play the Bell")
        self.bind("f1", "app.bell", description="Hello World")
        self.bind("f2", "app.bell", description="Do something")

    def compose(self):
        yield Footer()
