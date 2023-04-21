from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App
    from .message import Message
    from .message_pump import MessagePump
    from .screen import Screen


class NoActiveAppError(RuntimeError):
    """Runtime error raised if we try to retrieve the active app when there is none."""


active_app: ContextVar["App"] = ContextVar("active_app")
active_message_pump: ContextVar["MessagePump"] = ContextVar("active_message_pump")
prevent_message_types_stack: ContextVar[list[set[type[Message]]]] = ContextVar(
    "prevent_message_types_stack"
)
visible_screen_stack: ContextVar[list[Screen]] = ContextVar("visible_screen_stack")
"""A stack of visible screens (with background alpha < 1), used in the screen render process."""
