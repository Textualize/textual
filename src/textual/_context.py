from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App
    from .message import Message
    from .message_pump import MessagePump


class NoActiveAppError(RuntimeError):
    pass


active_app: ContextVar["App"] = ContextVar("active_app")
active_message_pump: ContextVar["MessagePump"] = ContextVar("active_message_pump")
prevent_message_types_stack: ContextVar[list[set[type[Message]]]] = ContextVar(
    "prevent_message_types_stack"
)
