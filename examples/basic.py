from textual.app import App
from textual.widget import Widget


class BasicApp(App):
    """A basic app demonstrating CSS"""

    def on_mount(self) -> None:
        """Build layout here."""

        self.view.mount(
            header=Widget(),
            content=Widget(),
            footer=Widget(),
            sidebar=Widget(),
        )


BasicApp.run(css_file="basic.css")
