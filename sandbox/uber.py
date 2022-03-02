from tkinter import Place
from textual.app import App
from textual import events
from textual.widgets import Placeholder
from textual.widget import Widget


class BasicApp(App):
    """Sandbox application used for testing/development by Textual developers"""

    def on_mount(self):
        """Build layout here."""

        uber2 = Widget()
        uber2.add_children(
            Placeholder(id="uber2-child1"),
            Placeholder(id="uber2-child2"),
        )

        self.mount(
            uber=Widget(
                Placeholder(id="child1"),
                Placeholder(id="child2"),
                Placeholder(id="child3"),
            ),
            uber2=uber2,
        )
        # self.panic(self.tree)

    async def on_key(self, event: events.Key) -> None:
        await self.dispatch_key(event)


BasicApp.run(css_file="uber.css", log="textual.log")
