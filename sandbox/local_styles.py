from textual.app import App
from textual.widgets import Placeholder
from textual.widget import Widget
from textual import events


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

    def key_a(self) -> bool | None:
        self.query("#footer").set_styles(text="on magenta").refresh()

        self.log(self["#footer"].styles.css)
        self.bell()
        self.refresh()

    def key_b(self) -> bool | None:
        self["#content"].set_styles("text: on magenta")


BasicApp.run(css_file="local_styles.css", log="textual.log")
