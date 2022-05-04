from textual import events
from textual.app import App
from textual.widget import Widget
from textual.widgets import Placeholder


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
        footer = self.get_child("footer")
        footer.set_styles(text="on magenta")

    def key_b(self) -> None:
        footer = self.get_child("footer")
        footer.set_styles("text: on green")

    def key_c(self) -> None:
        header = self.get_child("header")
        header.toggle_class("-highlight")
        self.log(header.styles)


BasicApp.run(css_path="local_styles.css", log_path="textual.log")
