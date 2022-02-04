from textual.app import App
from textual.widget import Widget


class BasicApp(App):
    """A basic app demonstrating CSS"""

    def on_load(self):
        """Bind keys here."""
        self.bind("tab", "toggle_class('#sidebar', '-active')")

    def on_mount(self):
        """Build layout here."""
        self.mount(
            header=Widget(),
            content=Widget(),
            footer=Widget(),
            sidebar=Widget(),
        )

        self.app.panic(repr(self.view.styles))


BasicApp.run(css_file="basic.css", watch_css=True, log="textual.log")
