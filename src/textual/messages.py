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
        yield "widget"

    def can_replace(self, message: Message) -> bool:
        return isinstance(message, UpdateMessage) and self.widget is message.widget


@rich.repr.auto
class LayoutMessage(Message, verbosity=3):
    def can_replace(self, message: Message) -> bool:
        return isinstance(message, LayoutMessage)
