from __future__ import annotations
from typing import TYPE_CHECKING

import rich.repr

from .message import Message


if TYPE_CHECKING:
    from .message_pump import MessagePump
    from .widget import Widget


@rich.repr.auto
class Update(Message, verbosity=3):
    def __init__(self, sender: MessagePump, widget: Widget):
        super().__init__(sender)
        self.widget = widget

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.sender
        yield self.widget

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Update):
            return self.widget == other.widget
        return NotImplemented

    def can_replace(self, message: Message) -> bool:
        # Update messages can replace update for the same widget
        return isinstance(message, Update) and self == message


@rich.repr.auto
class Layout(Message, verbosity=3):
    def can_replace(self, message: Message) -> bool:
        return isinstance(message, Layout)


@rich.repr.auto
class CursorMove(Message):
    def __init__(self, sender: MessagePump, line: int) -> None:
        self.line = line
        super().__init__(sender)


@rich.repr.auto
class StylesUpdated(Message):
    def __init__(self, sender: MessagePump) -> None:
        super().__init__(sender)

    def can_replace(self, message: Message) -> bool:
        return isinstance(message, StylesUpdated)


class Prompt(Message, system=True):
    """Used to 'wake up' an event loop."""

    def can_replace(self, message: Message) -> bool:
        return isinstance(message, Prompt)


class TerminalSupportsSynchronizedOutput(Message):
    """
    Used to make the App aware that the terminal emulator supports synchronised output.
    @link https://gist.github.com/christianparpart/d8a62cc1ab659194337d73e399004036
    """
