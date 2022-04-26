import random
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
        self.bind("o", "toggle_visibility")
        self.bind("p", "toggle_display")
        self.bind("f", "modify_focussed")
        self.bind("b", "toggle_border")

    async def on_mount(self):
        """Build layout here."""

        uber2 = Widget()
        uber2.add_children(
            Widget(id="uber2-child1"),
            Widget(id="uber2-child2"),
        )
        first_child = Placeholder(id="child1", classes={"list-item"})
        uber1 = Widget(
            first_child,
            Placeholder(id="child2", classes={"list-item"}),
            Placeholder(id="child3", classes={"list-item"}),
            Placeholder(classes={"list-item"}),
            Placeholder(classes={"list-item"}),
            Placeholder(classes={"list-item"}),
        )
        self.mount(uber1=uber1)
        await first_child.focus()

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

    def action_modify_focussed(self):
        """Increment height of focussed child, randomise border and bg color"""
        previous_height = self.focused.styles.height.value
        new_height = previous_height + 1
        self.focused.styles.height = self.focused.styles.height.copy_with(
            value=new_height
        )
        color = random.choice(["red", "green", "blue"])
        self.focused.styles.background = color
        self.focused.styles.border = ("dashed", color)

    def action_toggle_visibility(self):
        self.focused.visible = not self.focused.visible

    def action_toggle_display(self):
        # TODO: Doesn't work
        self.focused.display = not self.focused.display

    def action_toggle_border(self):
        self.focused.styles.border = [("solid", "red"), ("dashed", "white")]


BasicApp.run(css_file="uber.css", log="textual.log", log_verbosity=1)
