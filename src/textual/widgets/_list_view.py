from __future__ import annotations

from textual.reactive import reactive
from textual.containers import Container
from textual.message import Message
from textual.widget import Widget


class ListItem(Widget):
    pass


class ListView(Container):
    highlight_index = reactive(0)

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)

    class Highlighted(Message):
        def __init__(self, sender: ListView, widget: ListItem) -> None:
            super().__init__(sender)
            self.widget = widget

    class Selected(Message):
        def __init__(self, sender: ListView, widget: ListItem) -> None:
            super().__init__(sender)
            self.widget = widget
