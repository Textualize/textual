from __future__ import annotations
from typing import TYPE_CHECKING

import rich.repr

from .message import Message


if TYPE_CHECKING:
    from .message_pump import MessagePump
    from .widget import Widget


@rich.repr.auto
class UpdateMessage(Message):
    def __init__(
        self,
        sender: MessagePump,
        widget: Widget,
        offset_x: int = 0,
        offset_y: int = 0,
        reflow: bool = False,
    ):
        super().__init__(sender)
        self.widget = widget
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.reflow = reflow

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield self.sender
        yield "widget"
        yield "offset_x", self.offset_x, 0
        yield "offset_y", self.offset_y, 0
        yield "reflow", self.reflow, False

    def can_replace(self, message: Message) -> bool:
        return isinstance(message, UpdateMessage) and message.sender == self.sender


@rich.repr.auto
class LayoutMessage(Message):
    def can_replace(self, message: Message) -> bool:
        return isinstance(message, LayoutMessage) and message.sender == self.sender
