from __future__ import annotations

from textual.binding import Binding
from textual.geometry import clamp
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets._list_item import ListItem


class ListView(Widget, can_focus=True, can_focus_children=True):
    DEFAULT_CSS = """
    ListView {
        layout: vertical;
        overflow: auto;
    }
    """

    index = reactive(0)

    BINDINGS = [
        Binding("down", "down", "Down"),
        Binding("up", "up", "Up"),
    ]

    def __init__(
        self,
        *children: ListItem,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)

    def validate_index(self, index: int) -> int:
        last_index = len(self.children) - 1
        return clamp(index, 0, last_index)

    def watch_index(self, index: int) -> None:
        child = self.children[index]
        child.highlighted = True

    def action_down(self) -> None:
        self.index += 1

    def action_up(self) -> None:
        self.index -= 1

    class Highlighted(Message):
        def __init__(self, sender: ListView, item: ListItem) -> None:
            super().__init__(sender)
            self.item = item

    class Selected(Message):
        def __init__(self, sender: ListView, item: ListItem) -> None:
            super().__init__(sender)
            self.item = item
