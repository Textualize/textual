from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from textual.app import App
    from textual.message import Message
    from textual.message_pump import MessagePump
    from textual.screen import Screen


class NoActiveAppError(RuntimeError):
    """Runtime error raised if we try to retrieve the active app when there is none."""


active_app: ContextVar["App[Any]"] = ContextVar("active_app")
active_message_pump: ContextVar["MessagePump"] = ContextVar("active_message_pump")

prevent_message_types_stack: ContextVar[list[set[type[Message]]]] = ContextVar(
    "prevent_message_types_stack"
)
visible_screen_stack: ContextVar[list[Screen[object]]] = ContextVar(
    "visible_screen_stack"
)
"""A stack of visible screens (with background alpha < 1), used in the screen render process."""
message_hook: ContextVar[Callable[[Message], None]] = ContextVar("message_hook")
"""A callable that accepts a message. Used by App.run_test."""
