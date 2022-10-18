"""Sandbox app to test widget removal and focus-handing.

Written to help test changes made to solve:

  https://github.com/Textualize/textual/issues/939
"""

from textual.app import App
from textual.containers import Container
from textual.widgets import Static


class NonFocusParent(Static):
    def compose(self):
        yield Static("Test")


class SingleWidgetTester(App[None]):

    BINDINGS = [("a", "add_widget", "Add Widget"), ("d", "del_widget", "Delete Widget")]

    def compose(self):
        yield Container()

    def action_add_widget(self):
        self.query_one(Container).mount(NonFocusParent())

    def action_del_widget(self):
        candidates = self.query(NonFocusParent)
        if candidates:
            candidates.last().remove()


if __name__ == "__main__":
    SingleWidgetTester().run()
