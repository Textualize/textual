from __future__ import annotations

from textual.message import Message
from textual.widget import Widget


class ListItem(Widget):
    pass


class ListView(Widget):
    class Highlighted(Message):
        def __init__(self, sender: ListView, widget: ListItem) -> None:
            super().__init__(sender)
            self.widget = widget

    class Selected(Message):
        def __init__(self, sender: ListView, widget: ListItem) -> None:
            super().__init__(sender)
            self.widget = widget
