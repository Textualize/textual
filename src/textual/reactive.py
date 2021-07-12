from __future__ import annotations

from functools import partial
import sys
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Type,
    Union,
    TypeVar,
    TYPE_CHECKING,
)
from weakref import WeakSet

from . import events

from .message_pump import MessagePump
from ._types import MessageTarget

if TYPE_CHECKING:
    from .message import Message
    from .app import App
    from .widget import Widget

    Reactable = Union[Widget, App]

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


ReactiveType = TypeVar("ReactiveType")


class Reactive(Generic[ReactiveType]):
    """Reactive descriptor."""

    def __init__(
        self,
        default: ReactiveType,
        *,
        layout: bool = False,
        repaint: bool = True,
    ) -> None:
        self._default = default
        self.layout = layout
        self.repaint = repaint
        self._first = True

    def __set_name__(self, owner: Type[MessageTarget], name: str) -> None:
        self.name = name
        self.internal_name = f"__{name}"
        setattr(owner, self.internal_name, self._default)

    def __get__(self, obj: Reactable, obj_type: type[object]) -> ReactiveType:
        return getattr(obj, self.internal_name)

    def __set__(self, obj: Reactable, value: ReactiveType) -> None:

        name = self.name
        internal_name = f"__{name}"
        current_value = getattr(obj, internal_name, None)
        validate_function = getattr(obj, f"validate_{name}", None)
        if callable(validate_function):
            value = validate_function(value)

        if current_value != value or self._first:
            self._first = False
            setattr(obj, internal_name, value)

            self.check_watchers(obj, name)

            if self.layout:
                obj.require_layout()
            elif self.repaint:
                obj.require_repaint()

    @classmethod
    def check_watchers(cls, obj: Reactable, name: str) -> None:

        internal_name = f"__{name}"
        value = getattr(obj, internal_name)

        watch_function = getattr(obj, f"watch_{name}", None)
        if callable(watch_function):
            obj.post_message_no_wait(
                events.Callback(obj, callback=partial(watch_function, value))
            )

        watcher_name = f"__{name}_watchers"
        watchers = getattr(obj, watcher_name, ())
        for watcher in watchers:
            obj.post_message_no_wait(
                events.Callback(obj, callback=partial(watcher, value))
            )


def watch(
    obj: Reactable, attribute_name: str, callback: Callable[[Any], Awaitable]
) -> None:
    watcher_name = f"__{attribute_name}_watchers"
    if not hasattr(obj, watcher_name):
        setattr(obj, watcher_name, WeakSet())
    watchers = getattr(obj, watcher_name)
    watchers.add(callback)
    Reactive.check_watchers(obj, attribute_name)
