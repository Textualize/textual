from __future__ import annotations

from inspect import isawaitable
from functools import partial
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

from . import log
from . import events

from ._callback import count_parameters, invoke
from ._types import MessageTarget

if TYPE_CHECKING:
    from .app import App
    from .widget import Widget

    Reactable = Union[Widget, App]


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

        if hasattr(owner, f"compute_{name}"):
            try:
                computes = getattr(owner, "__computes")
            except AttributeError:
                computes = []
                setattr(owner, "__computes", computes)
            computes.append(name)

        self.name = name
        self.internal_name = f"__{name}"
        setattr(owner, self.internal_name, self._default)

    def __get__(self, obj: Reactable, obj_type: type[object]) -> ReactiveType:
        return getattr(obj, self.internal_name)

    def __set__(self, obj: Reactable, value: ReactiveType) -> None:

        name = self.name
        current_value = getattr(obj, self.internal_name, None)
        validate_function = getattr(obj, f"validate_{name}", None)
        if callable(validate_function):
            value = validate_function(value)

        if current_value != value or self._first:

            self._first = False
            setattr(obj, self.internal_name, value)
            self.check_watchers(obj, name, current_value)

            if self.layout:
                obj.refresh(layout=True)
            elif self.repaint:
                obj.refresh()

    @classmethod
    def check_watchers(cls, obj: Reactable, name: str, old_value: Any) -> None:

        internal_name = f"__{name}"
        value = getattr(obj, internal_name)

        async def update_watcher(
            obj: Reactable, watch_function: Callable, old_value: Any, value: Any
        ) -> None:
            _rich_traceback_guard = True
            if count_parameters(watch_function) == 2:
                watch_result = watch_function(old_value, value)
            else:
                watch_result = watch_function(value)
            if isawaitable(watch_result):
                await watch_result
            await Reactive.compute(obj)

        watch_function = getattr(obj, f"watch_{name}", None)
        if callable(watch_function):
            obj.post_message_no_wait(
                events.Callback(
                    obj,
                    callback=partial(
                        update_watcher, obj, watch_function, old_value, value
                    ),
                )
            )

        watcher_name = f"__{name}_watchers"
        watchers = getattr(obj, watcher_name, ())
        for watcher in watchers:
            obj.post_message_no_wait(
                events.Callback(
                    obj,
                    callback=partial(update_watcher, obj, watcher, old_value, value),
                )
            )

    @classmethod
    async def compute(cls, obj: Reactable) -> None:
        _rich_traceback_guard = True
        computes = getattr(obj, "__computes", [])
        for compute in computes:
            try:
                compute_method = getattr(obj, f"compute_{compute}")
            except AttributeError:
                continue
            value = await invoke(compute_method)
            setattr(obj, compute, value)


def watch(
    obj: Reactable, attribute_name: str, callback: Callable[[Any], Awaitable[None]]
) -> None:
    watcher_name = f"__{attribute_name}_watchers"
    current_value = getattr(obj, attribute_name, None)
    if not hasattr(obj, watcher_name):
        setattr(obj, watcher_name, set())
    watchers = getattr(obj, watcher_name)
    watchers.add(callback)
    Reactive.check_watchers(obj, attribute_name, current_value)
