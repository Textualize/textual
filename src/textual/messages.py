from __future__ import annotations
from typing import TYPE_CHECKING

import rich.repr

from .message import Message


if TYPE_CHECKING:
    from .message_pump import MessagePump
    from .widget import Widget


@rich.repr.auto
class UpdateMessage(Message, verbosity=3):
    def __init__(self, sender: MessagePump, widget: Widget, layout: bool = False):
        super().__init__(sender)
        self.widget = widget
        self.layout = layout

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.sender
        yield self.widget

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UpdateMessage):
            return self.widget == other.widget and self.layout == other.layout
        return NotImplemented

    def can_replace(self, message: Message) -> bool:
        return isinstance(message, UpdateMessage) and self == message


@rich.repr.auto
class LayoutMessage(Message, verbosity=3):
    def can_replace(self, message: Message) -> bool:
        return isinstance(message, LayoutMessage)


@rich.repr.auto
class CursorMoveMessage(Message, bubble=True):
    def __init__(self, sender: MessagePump, line: int) -> None:
        self.line = line
        super().__init__(sender)
