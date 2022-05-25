from typing import TYPE_CHECKING

from contextvars import ContextVar

if TYPE_CHECKING:
    from .app import App


class NoActiveAppError(RuntimeError):
    pass


active_app: ContextVar["App"] = ContextVar("active_app")
