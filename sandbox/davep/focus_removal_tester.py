"""Focus removal tester.

https://github.com/Textualize/textual/issues/939
"""

from textual.app import App
from textual.containers import Container
from textual.widgets import Static, Header, Footer, Button


class NonFocusParent(Static):
    def compose(self):
        yield Button("Do Not Press")
        yield Static("Test")
        yield Button("Really Do Not Press")


class FocusRemovalTester(App[None]):

    BINDINGS = [("a", "add_widget", "Add Widget"), ("d", "del_widget", "Delete Widget")]

    def compose(self):
        yield Header()
        yield Container()
        yield Footer()

    def action_add_widget(self):
        self.query_one(Container).mount(NonFocusParent())

    def action_del_widget(self):
        candidates = self.query(NonFocusParent)
        if candidates:
            candidates.last().remove()


if __name__ == "__main__":
    FocusRemovalTester().run()
