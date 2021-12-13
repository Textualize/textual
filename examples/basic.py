from textual.app import App
from textual.widget import Widget


class BasicApp(App):
    """A basic app demonstrating CSS"""

    def on_load(self):
        self.bind("t", "toggle('#sidebar', '-active')")

    def on_mount(self):
        """Build layout here."""
        self.mount(
            header=Widget(),
            content=Widget(),
            footer=Widget(),
            sidebar=Widget(),
        )


BasicApp.run(log="textual.log", css_file="basic.css", log_verbosity=3)
