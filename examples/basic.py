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
            sidebar=Widget(
                Widget(classes={"title"}),
                Widget(classes={"user"}),
                Widget(classes={"content"}),
            ),
        )

    async def on_key(self, event) -> None:
        await self.dispatch_key(event)

    def key_d(self):
        self.dark = not self.dark

    def key_x(self):
        self.panic(self.tree)


BasicApp.run(css_file="basic.css", watch_css=True, log="textual.log")
