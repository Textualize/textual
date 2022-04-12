import time

from textual.app import App
from textual import events
from textual.widgets import Placeholder
from textual.widget import Widget


class BasicApp(App):
    """Sandbox application used for testing/development by Textual developers"""

    def on_load(self):
        self.bind("q", "quit", "Quit")
        self.bind("d", "dump")
        self.bind("t", "log_tree")
        self.bind("p", "print")

    def on_mount(self):
        """Build layout here."""

        uber2 = Widget()
        uber2.add_children(
            Widget(id="uber2-child1"),
            Widget(id="uber2-child2"),
        )
        uber1 = Widget(
            Placeholder(id="child1", classes={"list-item"}),
            Placeholder(id="child2", classes={"list-item"}),
            Placeholder(id="child3", classes={"list-item"}),
            Placeholder(classes={"list-item"}),
            Placeholder(classes={"list-item"}),
            Placeholder(classes={"list-item"}),
        )
        self.mount(uber1=uber1)

    async def on_key(self, event: events.Key) -> None:
        await self.dispatch_key(event)

    def action_quit(self):
        self.panic(self.screen.tree)

    def action_dump(self):
        self.panic(str(self.app.registry))

    def action_log_tree(self):
        self.log(self.screen.tree)

    def action_print(self):
        print("Hello, world!", "another", self.screen.tree)
        print("A new print statement")


BasicApp.run(css_file="uber.css", log="textual.log", log_verbosity=1)

# if __name__ == '__main__':
#     print(b"Hello, world!", "another", end="")
#     time.sleep(5)
