from __future__ import annotations

import weakref
from contextvars import ContextVar, Token
from typing import TYPE_CHECKING, Callable, Generic, TypeVar, overload

if TYPE_CHECKING:
    from .app import App
    from .message import Message
    from .message_pump import MessagePump
    from .screen import Screen


class NoActiveAppError(RuntimeError):
    """Runtime error raised if we try to retrieve the active app when there is none."""


ContextVarType = TypeVar("ContextVarType")
DefaultType = TypeVar("DefaultType")


class ContextDefault:
    pass


_context_default = ContextDefault()


class TextualContextVar(Generic[ContextVarType]):
    """Like ContextVar but doesn't hold on to references."""

    def __init__(self, name: str) -> None:
        self._context_var: ContextVar[weakref.ReferenceType[ContextVarType]] = (
            ContextVar(name)
        )

    @overload
    def get(self) -> ContextVarType: ...

    @overload
    def get(self, default: DefaultType) -> ContextVarType | DefaultType: ...

    def get(
        self, default: DefaultType | ContextDefault = _context_default
    ) -> ContextVarType | DefaultType:
        try:
            value_ref = self._context_var.get()
        except LookupError:
            if isinstance(default, ContextDefault):
                raise
            return default
        value = value_ref()
        if value is None:
            if isinstance(default, ContextDefault):
                raise LookupError(value)
            return default
        return value

    def set(self, value: ContextVarType) -> object:
        return self._context_var.set(weakref.ref(value))

    def reset(self, token: Token[weakref.ReferenceType[ContextVarType]]) -> None:
        self._context_var.reset(token)


active_app: TextualContextVar["App[object]"] = TextualContextVar("active_app")
active_message_pump: TextualContextVar["MessagePump"] = TextualContextVar(
    "active_message_pump"
)

prevent_message_types_stack: ContextVar[list[set[type[Message]]]] = ContextVar(
    "prevent_message_types_stack"
)
visible_screen_stack: ContextVar[list[Screen[object]]] = ContextVar(
    "visible_screen_stack"
)
"""A stack of visible screens (with background alpha < 1), used in the screen render process."""
message_hook: TextualContextVar[Callable[[Message], None]] = TextualContextVar(
    "message_hook"
)
"""A callable that accepts a message. Used by App.run_test."""
