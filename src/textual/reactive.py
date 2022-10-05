from __future__ import annotations

from functools import partial
from inspect import isawaitable
from typing import TYPE_CHECKING, Any, Callable, Generic, Type, TypeVar, Union
from weakref import WeakSet


from . import events
from ._callback import count_parameters, invoke
from ._types import MessageTarget

if TYPE_CHECKING:
    from .app import App
    from .widget import Widget

    Reactable = Union[Widget, App]


ReactiveType = TypeVar("ReactiveType", covariant=True)


T = TypeVar("T")


class Reactive(Generic[ReactiveType]):
    """Reactive descriptor.

    Args:
        default (ReactiveType | Callable[[], ReactiveType]): A default value or callable that returns a default.
        layout (bool, optional): Perform a layout on change. Defaults to False.
        repaint (bool, optional): Perform a repaint on change. Defaults to True.
        init (bool, optional): Call watchers on initialize (post mount). Defaults to False.

    """

    def __init__(
        self,
        default: ReactiveType | Callable[[], ReactiveType],
        *,
        layout: bool = False,
        repaint: bool = True,
        init: bool = False,
    ) -> None:
        self._default = default
        self._layout = layout
        self._repaint = repaint
        self._init = init

    @classmethod
    def init(
        cls,
        default: ReactiveType | Callable[[], ReactiveType],
        *,
        layout: bool = False,
        repaint: bool = True,
    ) -> Reactive:
        """A reactive variable that calls watchers and compute on initialize (post mount).

        Args:
            default (ReactiveType | Callable[[], ReactiveType]): A default value or callable that returns a default.
            layout (bool, optional): Perform a layout on change. Defaults to False.
            repaint (bool, optional): Perform a repaint on change. Defaults to True.

        Returns:
            Reactive: A Reactive instance which calls watchers or initialize.
        """
        return cls(default, layout=layout, repaint=repaint, init=True)

    @classmethod
    def var(
        cls,
        default: ReactiveType | Callable[[], ReactiveType],
    ) -> Reactive:
        """A reactive variable that doesn't update or layout.

        Args:
            default (ReactiveType | Callable[[], ReactiveType]):  A default value or callable that returns a default.

        Returns:
            Reactive: A Reactive descriptor.
        """
        return cls(default, layout=False, repaint=False, init=True)

    @classmethod
    async def initialize_object(cls, obj: object) -> None:
        """Call any watchers / computes for the first time.

        Args:
            obj (Reactable): An object with Reactive descriptors
        """

        startswith = str.startswith
        for key in obj.__class__.__dict__.keys():
            if startswith(key, "_init_"):
                name = key[6:]
                if not hasattr(obj, name):
                    default = getattr(obj, key)
                    setattr(obj, name, default() if callable(default) else default)

    def __set_name__(self, owner: Type[MessageTarget], name: str) -> None:

        if hasattr(owner, f"compute_{name}"):
            try:
                computes = getattr(owner, "__computes")
            except AttributeError:
                computes = []
                setattr(owner, "__computes", computes)
            computes.append(name)

        self.name = name
        self.internal_name = f"_reactive_{name}"
        default = self._default

        if self._init:
            setattr(owner, f"_init_{name}", default)
        else:
            setattr(
                owner, self.internal_name, default() if callable(default) else default
            )

    def __get__(self, obj: Reactable, obj_type: type[object]) -> ReactiveType:
        return getattr(obj, self.internal_name)

    def __set__(self, obj: Reactable, value: ReactiveType) -> None:
        name = self.name
        current_value = getattr(obj, self.internal_name, None)
        validate_function = getattr(obj, f"validate_{name}", None)
        first_set = getattr(obj, f"__first_set_{self.internal_name}", True)
        if callable(validate_function) and not first_set:
            value = validate_function(value)
        if current_value != value or first_set:
            setattr(obj, f"__first_set_{self.internal_name}", False)
            setattr(obj, self.internal_name, value)
            self._check_watchers(obj, name, current_value, first_set=first_set)
            if self._layout or self._repaint:
                obj.refresh(repaint=self._repaint, layout=self._layout)

    @classmethod
    def _check_watchers(
        cls, obj: Reactable, name: str, old_value: Any, first_set: bool = False
    ) -> None:

        internal_name = f"_reactive_{name}"
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
            await Reactive._compute(obj)

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

        if not first_set:
            obj.post_message_no_wait(
                events.Callback(obj, callback=partial(Reactive._compute, obj))
            )

    @classmethod
    async def _compute(cls, obj: Reactable) -> None:
        _rich_traceback_guard = True
        computes = getattr(obj, "__computes", [])
        for compute in computes:
            try:
                compute_method = getattr(obj, f"compute_{compute}")
            except AttributeError:
                continue

            value = await invoke(compute_method)
            setattr(obj, compute, value)


class reactive(Reactive[ReactiveType]):
    """Create a reactive attribute.

    Args:
        default (ReactiveType | Callable[[], ReactiveType]): A default value or callable that returns a default.
        layout (bool, optional): Perform a layout on change. Defaults to False.
        repaint (bool, optional): Perform a repaint on change. Defaults to True.
        init (bool, optional): Call watchers on initialize (post mount). Defaults to True.

    """

    def __init__(
        self,
        default: ReactiveType | Callable[[], ReactiveType],
        *,
        layout: bool = False,
        repaint: bool = True,
        init: bool = True,
    ) -> None:
        super().__init__(default, layout=layout, repaint=repaint, init=init)


class var(Reactive[ReactiveType]):
    """Create a reactive attribute (with no auto-refresh).

    Args:
        default (ReactiveType | Callable[[], ReactiveType]): A default value or callable that returns a default.
    """

    def __init__(self, default: ReactiveType | Callable[[], ReactiveType]) -> None:
        super().__init__(default, layout=False, repaint=False, init=True)


def watch(
    obj: Reactable, attribute_name: str, callback: Callable[[Any], object]
) -> None:
    """Watch a reactive variable on an object.

    Args:
        obj (Reactable): The parent object.
        attribute_name (str): The attribute to watch.
        callback (Callable[[Any], object]): A callable to call when the attribute changes.
    """
    watcher_name = f"__{attribute_name}_watchers"
    current_value = getattr(obj, attribute_name, None)
    if not hasattr(obj, watcher_name):
        setattr(obj, watcher_name, WeakSet())
    watchers = getattr(obj, watcher_name)
    watchers.add(callback)
    Reactive._check_watchers(obj, attribute_name, current_value)
