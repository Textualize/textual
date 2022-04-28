import sys

from textual import events
from textual.app import App
from textual.widget import Widget
from textual.widgets import Placeholder


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
            Placeholder(id="child1", classes="list-item"),
            Placeholder(id="child2", classes="list-item"),
            Placeholder(id="child3", classes="list-item"),
            Placeholder(classes="list-item"),
            Placeholder(classes="list-item"),
            Placeholder(classes="list-item"),
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
        print(
            "Printed using builtin [b blue]print[/] function:",
            self.screen.tree,
            sep=" - ",
        )
        print(1234, 5678)

        sys.stdout.write("abcdef")


app = BasicApp(css_file="uber.css", log="textual.log", log_verbosity=1)

if __name__ == "__main__":
    app.run()
