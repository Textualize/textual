from textual.app import App
from textual import events
from textual.widgets import Placeholder
from textual.widget import Widget


class BasicApp(App):
    """Sandbox application used for testing/development by Textual developers"""

    def on_mount(self):
        """Build layout here."""
        self.mount(uber=Placeholder())

    async def on_key(self, event: events.Key) -> None:
        await self.dispatch_key(event)


BasicApp.run(css_file="uber.css", log="textual.log")
