"""

This module contains the `Reactive` class which implements [reactivity](/guide/reactivity/).
"""

from __future__ import annotations

from functools import partial
from inspect import isawaitable
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Type,
    TypeVar,
    cast,
    overload,
)

import rich.repr

from textual import events
from textual._callback import count_parameters
from textual._types import (
    MessageTarget,
    WatchCallbackBothValuesType,
    WatchCallbackNewValueType,
    WatchCallbackNoArgsType,
    WatchCallbackType,
)

if TYPE_CHECKING:
    from textual.dom import DOMNode

    Reactable = DOMNode

ReactiveType = TypeVar("ReactiveType")
ReactableType = TypeVar("ReactableType", bound="DOMNode")


class _Mutated:
    """A wrapper to indicate a value was mutated."""

    def __init__(self, value: Any) -> None:
        self.value = value


class ReactiveError(Exception):
    """Base class for reactive errors."""


class TooManyComputesError(ReactiveError):
    """Raised when an attribute has public and private compute methods."""


async def await_watcher(obj: Reactable, awaitable: Awaitable[object]) -> None:
    """Coroutine to await an awaitable returned from a watcher"""
    _rich_traceback_omit = True
    await awaitable
    # Watcher may have changed the state, so run compute again
    obj.post_message(events.Callback(callback=partial(Reactive._compute, obj)))


def invoke_watcher(
    watcher_object: Reactable,
    watch_function: WatchCallbackType,
    old_value: object,
    value: object,
) -> None:
    """Invoke a watch function.

    Args:
        watcher_object: The object watching for the changes.
        watch_function: A watch function, which may be sync or async.
        old_value: The old value of the attribute.
        value: The new value of the attribute.
    """
    _rich_traceback_omit = True

    param_count = count_parameters(watch_function)

    with watcher_object._context():
        if param_count == 2:
            watch_result = cast(WatchCallbackBothValuesType, watch_function)(
                old_value, value
            )
        elif param_count == 1:
            watch_result = cast(WatchCallbackNewValueType, watch_function)(value)
        else:
            watch_result = cast(WatchCallbackNoArgsType, watch_function)()
        if isawaitable(watch_result):
            # Result is awaitable, so we need to await it within an async context
            watcher_object.call_next(
                partial(await_watcher, watcher_object, watch_result)
            )


@rich.repr.auto
class Reactive(Generic[ReactiveType]):
    """Reactive descriptor.

    Args:
        default: A default value or callable that returns a default.
        layout: Perform a layout on change.
        repaint: Perform a repaint on change.
        init: Call watchers on initialize (post mount).
        always_update: Call watchers even when the new value equals the old value.
        compute: Run compute methods when attribute is changed.
        recompose: Compose the widget again when the attribute changes.
        bindings: Refresh bindings when the reactive changes.
    """

    _reactives: ClassVar[dict[str, object]] = {}

    def __init__(
        self,
        default: ReactiveType | Callable[[], ReactiveType],
        *,
        layout: bool = False,
        repaint: bool = True,
        init: bool = False,
        always_update: bool = False,
        compute: bool = True,
        recompose: bool = False,
        bindings: bool = False,
    ) -> None:
        self._default = default
        self._layout = layout
        self._repaint = repaint
        self._init = init
        self._always_update = always_update
        self._run_compute = compute
        self._recompose = recompose
        self._bindings = bindings
        self._owner: Type[MessageTarget] | None = None
        self.name: str

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, self._default
        yield "layout", self._layout, False
        yield "repaint", self._repaint, True
        yield "init", self._init, False
        yield "always_update", self._always_update, False
        yield "compute", self._run_compute, True
        yield "recompose", self._recompose, False
        yield "bindings", self._bindings, False
        yield "name", getattr(self, "name", None), None

    @classmethod
    def _clear_watchers(cls, obj: Reactable) -> None:
        """Clear any watchers on a given object.

        Args:
            obj: A reactive object.
        """
        try:
            getattr(obj, "__watchers").clear()
        except AttributeError:
            pass

    @property
    def owner(self) -> Type[MessageTarget]:
        """The owner (class) where the reactive was declared."""
        assert self._owner is not None
        return self._owner

    def _initialize_reactive(self, obj: Reactable, name: str) -> None:
        """Initialized a reactive attribute on an object.

        Args:
            obj: An object with reactive attributes.
            name: Name of attribute.
        """
        _rich_traceback_omit = True
        internal_name = f"_reactive_{name}"
        if hasattr(obj, internal_name):
            # Attribute already has a value
            return

        compute_method = getattr(obj, self.compute_name, None)
        if compute_method is not None and self._init:
            default = compute_method()
        else:
            default_or_callable = self._default
            default = (
                default_or_callable()
                if callable(default_or_callable)
                else default_or_callable
            )
        setattr(obj, internal_name, default)
        if self._init:
            self._check_watchers(obj, name, default)

    @classmethod
    def _initialize_object(cls, obj: Reactable) -> None:
        """Set defaults and call any watchers / computes for the first time.

        Args:
            obj: An object with Reactive descriptors
        """
        _rich_traceback_omit = True
        for name, reactive in obj._reactives.items():
            reactive._initialize_reactive(obj, name)

    @classmethod
    def _reset_object(cls, obj: object) -> None:
        """Reset reactive structures on object (to avoid reference cycles).

        Args:
            obj: A reactive object.
        """
        getattr(obj, "__watchers", {}).clear()
        getattr(obj, "__computes", []).clear()

    def __set_name__(self, owner: Type[MessageTarget], name: str) -> None:
        # Check for compute method
        self._owner = owner
        public_compute = f"compute_{name}"
        private_compute = f"_compute_{name}"
        compute_name = (
            private_compute if hasattr(owner, private_compute) else public_compute
        )
        if hasattr(owner, compute_name):
            # Compute methods are stored in a list called `__computes`
            try:
                computes = getattr(owner, "__computes")
            except AttributeError:
                computes = []
                setattr(owner, "__computes", computes)
            computes.append(name)

        # The name of the attribute
        self.name = name
        # The internal name where the attribute's value is stored
        self.internal_name = f"_reactive_{name}"
        self.compute_name = compute_name
        default = self._default
        setattr(owner, f"_default_{name}", default)

    if TYPE_CHECKING:

        @overload
        def __get__(
            self: Reactive[ReactiveType],
            obj: ReactableType,
            obj_type: type[ReactableType],
        ) -> ReactiveType: ...

        @overload
        def __get__(
            self: Reactive[ReactiveType], obj: None, obj_type: type[ReactableType]
        ) -> Reactive[ReactiveType]: ...

    def __get__(
        self: Reactive[ReactiveType],
        obj: Reactable | None,
        obj_type: type[ReactableType],
    ) -> Reactive[ReactiveType] | ReactiveType:
        _rich_traceback_omit = True
        if obj is None:
            # obj is None means we are invoking the descriptor via the class, and not the instance
            return self
        if not hasattr(obj, "id"):
            raise ReactiveError(
                f"Node is missing data; Check you are calling super().__init__(...) in the {obj.__class__.__name__}() constructor, before getting reactives."
            )
        if not hasattr(obj, internal_name := self.internal_name):
            self._initialize_reactive(obj, self.name)

        if hasattr(obj, self.compute_name):
            value: ReactiveType
            old_value = getattr(obj, internal_name)
            value = getattr(obj, self.compute_name)()
            setattr(obj, internal_name, value)
            self._check_watchers(obj, self.name, old_value)
            return value
        else:
            return getattr(obj, internal_name)

    def _set(self, obj: Reactable, value: ReactiveType, always: bool = False) -> None:
        _rich_traceback_omit = True

        if not hasattr(obj, "_id"):
            raise ReactiveError(
                f"Node is missing data; Check you are calling super().__init__(...) in the {obj.__class__.__name__}() constructor, before setting reactives."
            )

        if isinstance(value, _Mutated):
            value = value.value
            always = True

        self._initialize_reactive(obj, self.name)

        if hasattr(obj, self.compute_name):
            raise AttributeError(
                f"Can't set {obj}.{self.name!r}; reactive attributes with a compute method are read-only"
            )

        name = self.name
        current_value = getattr(obj, name)
        # Check for private and public validate functions.
        private_validate_function = getattr(obj, f"_validate_{name}", None)
        if callable(private_validate_function):
            value = private_validate_function(value)
        public_validate_function = getattr(obj, f"validate_{name}", None)
        if callable(public_validate_function):
            value = public_validate_function(value)
        # If the value has changed, or this is the first time setting the value
        if always or self._always_update or current_value != value:
            # Store the internal value
            setattr(obj, self.internal_name, value)

            # Check all watchers
            self._check_watchers(obj, name, current_value)

            if self._run_compute:
                self._compute(obj)

            if self._bindings:
                obj.refresh_bindings()

            # Refresh according to descriptor flags
            if self._layout or self._repaint or self._recompose:
                obj.refresh(
                    repaint=self._repaint,
                    layout=self._layout,
                    recompose=self._recompose,
                )

    def __set__(self, obj: Reactable, value: ReactiveType) -> None:
        _rich_traceback_omit = True

        self._set(obj, value)

    @classmethod
    def _check_watchers(cls, obj: Reactable, name: str, old_value: Any) -> None:
        """Check watchers, and call watch methods / computes

        Args:
            obj: The reactable object.
            name: Attribute name.
            old_value: The old (previous) value of the attribute.
        """
        _rich_traceback_omit = True
        # Get the current value.
        internal_name = f"_reactive_{name}"
        value = getattr(obj, internal_name)

        private_watch_function = getattr(obj, f"_watch_{name}", None)
        if callable(private_watch_function):
            invoke_watcher(obj, private_watch_function, old_value, value)

        public_watch_function = getattr(obj, f"watch_{name}", None)
        if callable(public_watch_function):
            invoke_watcher(obj, public_watch_function, old_value, value)

        # Process "global" watchers
        watchers: list[tuple[Reactable, WatchCallbackType]]
        watchers = getattr(obj, "__watchers", {}).get(name, [])
        # Remove any watchers for reactables that have since closed
        if watchers:
            watchers[:] = [
                (reactable, callback)
                for reactable, callback in watchers
                if not reactable._closing
            ]
            for reactable, callback in watchers:
                with reactable.prevent(*obj._prevent_message_types_stack[-1]):
                    invoke_watcher(reactable, callback, old_value, value)

    @classmethod
    def _compute(cls, obj: Reactable) -> None:
        """Invoke all computes.

        Args:
            obj: Reactable object.
        """
        _rich_traceback_guard = True
        for compute in obj._reactives.keys() & obj._computes:
            try:
                compute_method = getattr(obj, f"compute_{compute}")
            except AttributeError:
                try:
                    compute_method = getattr(obj, f"_compute_{compute}")
                except AttributeError:
                    continue
            current_value = getattr(
                obj, f"_reactive_{compute}", getattr(obj, f"_default_{compute}", None)
            )
            value = compute_method()
            setattr(obj, f"_reactive_{compute}", value)
            if value != current_value:
                cls._check_watchers(obj, compute, current_value)


class reactive(Reactive[ReactiveType]):
    """Create a reactive attribute.

    Args:
        default: A default value or callable that returns a default.
        layout: Perform a layout on change.
        repaint: Perform a repaint on change.
        init: Call watchers on initialize (post mount).
        always_update: Call watchers even when the new value equals the old value.
        bindings: Refresh bindings when the reactive changes.
    """

    def __init__(
        self,
        default: ReactiveType | Callable[[], ReactiveType],
        *,
        layout: bool = False,
        repaint: bool = True,
        init: bool = True,
        always_update: bool = False,
        recompose: bool = False,
        bindings: bool = False,
    ) -> None:
        super().__init__(
            default,
            layout=layout,
            repaint=repaint,
            init=init,
            always_update=always_update,
            recompose=recompose,
            bindings=bindings,
        )


class var(Reactive[ReactiveType]):
    """Create a reactive attribute (with no auto-refresh).

    Args:
        default: A default value or callable that returns a default.
        init: Call watchers on initialize (post mount).
        always_update: Call watchers even when the new value equals the old value.
        bindings: Refresh bindings when the reactive changes.
    """

    def __init__(
        self,
        default: ReactiveType | Callable[[], ReactiveType],
        init: bool = True,
        always_update: bool = False,
        bindings: bool = False,
    ) -> None:
        super().__init__(
            default,
            layout=False,
            repaint=False,
            init=init,
            always_update=always_update,
            bindings=bindings,
        )


def _watch(
    node: DOMNode,
    obj: Reactable,
    attribute_name: str,
    callback: WatchCallbackType,
    *,
    init: bool = True,
) -> None:
    """Watch a reactive variable on an object.

    Args:
        node: The node that created the watcher.
        obj: The parent object.
        attribute_name: The attribute to watch.
        callback: A callable to call when the attribute changes.
        init: True to call watcher initialization.
    """
    if not hasattr(obj, "__watchers"):
        setattr(obj, "__watchers", {})
    watchers: dict[str, list[tuple[Reactable, WatchCallbackType]]]
    watchers = getattr(obj, "__watchers")
    watcher_list = watchers.setdefault(attribute_name, [])
    if any(callback == callback_from_list for _, callback_from_list in watcher_list):
        return
    if init:
        current_value = getattr(obj, attribute_name, None)
        invoke_watcher(obj, callback, current_value, current_value)
    watcher_list.append((node, callback))
