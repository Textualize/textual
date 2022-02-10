from textual.app import App
from textual import events
from textual.widgets import Placeholder
from textual.widget import Widget


class BasicApp(App):
    """Sandbox application used for testing/development by Textual developers"""

    def on_mount(self):
        """Build layout here."""
        self.mount(
            header=Widget(),
            content=Placeholder(),
            footer=Widget(),
            sidebar=Widget(),
        )

    async def on_key(self, event: events.Key) -> None:
        await self.dispatch_key(event)

    def key_a(self) -> None:
        self.query("#footer").set_styles(text="on magenta")

    def key_b(self) -> None:
        self["#footer"].set_styles("text: on green")


BasicApp.run(css_file="local_styles.css", log="textual.log")
