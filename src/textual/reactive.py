from __future__ import annotations

from functools import partial
from inspect import isawaitable
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    Type,
    TypeVar,
)

import rich.repr

from . import events
from ._callback import count_parameters

if TYPE_CHECKING:
    from .dom import DOMNode

    Reactable = DOMNode

ReactiveType = TypeVar("ReactiveType")

"""
Throughout this module:

A "reactable" (an instance of `Reactable`) is an object holding reactive attributes.

A "reactive" (an instance of `Reactive`) is a reactive attribute. There is an
instance of `Reactive` for every reactive attribute of _class_ (not instance!) of a
reactable object; so if 2 reactable objects of the same class had 3 reactive
attributes each, there would be a total of 3 `Reactive` instances, not 6.



To illustrate the mechanism, let us walk through an example:

```
class MyWidget(Static):
    foo = Reactive(1)
    bar = Reactive(2)
```

When class `MyWidget` is deinfed (in Python parlance it is actually created, but
let's not fuss) two instances of `Reactive` are created, hence `Reactive.__init__`
is invoked twice.

After both instances are created, Python invokes `Reactive.__set_name__` on each,
telling the first instance that it is called "foo" and is in the class `MyWidget`,
and telling the second instance that it is called "bar" and is also in the class
`MyWidget`.

Also during this stage, `DOMNode.__init_subclass__` is invoked (all reactable class
inherit from DOMNode), and the code there sets up a map in `MyWidget` which reads:

```
MyWidget._reactives = {
    "foo": <the first Reactive instance>,
    "bar": <the second Reactive instance>,
}
```

At this point, no instances of `MyWidget` have been created.

At some later point, we create an instance of `MyWidget`:

```
w = MyWidget()
```

Nothing magical relating to reactives occurs at this point. `MyWidget.__init__` is
simply invoked and nothing more.

At a later point, `w` is mounted (yielded from `Compose()`, or throught `.mount())
At this stage, code in `DOMNode` calls `_initialize_reactable_object(w)`, setting up
attributes on `w` to hold the actual values of `w.foo` and `w.bar`. This is the
first time that something specific to an instance of a reactive attribute on a
specific reactable object occurs.

At a later point still, the following may happen:

```
x = w.foo
w.bar = 3
```

When `w.foo` is accessed, Python invokes `__get__` on the Reactive instance for
`foo` ("the first instance" from above), passing it `w` as a parameter. The code in
`__get__` can then access the attributes on `w` set up during
`_initialize_reactable_object` mentioned above.

When `w.bar` is assigned to, Python invokes `__get__` on the Reactive instance for
`bar` ("the second instance" from above), passing it `w` as a parameter. The code in
`__set__` can then access the attributes on `w` set up during
`_initialize_reactable_object` mentioned above.

Setting a reactive attribute may also trigger a reactable-wide recompute of reactive
attributes, which is done by the code in `__set__` invoking
`_recompute_reactable_object`.

At a much later stage, when `w` is no longer needed, code in `DOMNode` calls
`_reset_reactable_object(w)`.


We see thus the following categories of methods involved:

    * once per reactive attribute of a reactable class
        `Reactive.__init__`
        `Reactive.__set_name__`

    * once per reactable class
        `DOMNode.__init_subclass__`

    * once per reactable object
        `Reactive._initialize_reactable_object`
        `Reactive._reset_reactable_object`

    * once per reactive attribute on a specific reactable object:
        `Reactive._initialize_reactive`

    * every access to a specific reactive attribute of a specific reactable object:
        `__get__`
        `__set__`
        `_set_reactive_inner`
        `_compute_reactive`,
        `_notify_reactive_watchers`
        `_compute_reactable_object`
"""


@rich.repr.auto
class Reactive(Generic[ReactiveType]):
    """Reactive descriptor.

    Args:
        default: A default value or callable that returns a default.
        layout: Perform a layout on change. Defaults to False.
        repaint: Perform a repaint on change. Defaults to True.
        init: Call watchers on initialize (post mount). Defaults to False.
        always_update: Call watchers even when the new value equals the old value. Defaults to False.
        compute: Run compute methods when attribute is changed. Defaults to True.
    """

    def __init__(
        self,
        default: ReactiveType | Callable[[], ReactiveType],
        *,
        layout: bool = False,
        repaint: bool = True,
        init: bool = False,
        always_update: bool = False,
        compute: bool = True,
    ) -> None:
        self._default = default
        self._layout = layout
        self._repaint = repaint
        self._init = init
        self._always_update = always_update
        self._trigger_object_compute = compute

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._default
        yield "layout", self._layout
        yield "repaint", self._repaint
        yield "init", self._init
        yield "always_update", self._always_update
        yield "compute", self._trigger_object_compute

    def __set_name__(self, owner: Type[Reactable], name: str) -> None:
        # The name of the attribute
        self.name = name
        # The internal name where the attribute's value is stored
        self.internal_name = f"_reactive_{name}"
        # Corresponding compute, watch and validate methods, if exist
        # NOTE that these are all instance methods, but are stored here
        # bound to the reactable class (and not the instance, which at
        # this point is unknown.). This means that invoking them must
        # supply a `self` parameter as well.
        self.compute_function = getattr(owner, f"compute_{name}", None)
        self.validate_function = getattr(owner, f"validate_{name}", None)
        self.watch_function = getattr(owner, f"watch_{name}", None)

    def __get__(self, obj: Reactable, obj_type: type | None = None) -> ReactiveType:
        """Return the cached value of the reactive attribute.

        Args:
            obj: An object with reactive attributes.
            obj_type: used; Python will pass a type here if accessing the
                the reactive on a class rather than on an instance.
        """
        _rich_traceback_omit = True
        self._initialize_reactive(obj)
        value: ReactiveType = getattr(obj, self.internal_name)
        return value

    def __set__(self, obj: Reactable, value: ReactiveType) -> None:
        """Set the value of the reactive attribute, invoking any
        validation and watch methods.

        Then, maybe trigger object-wide recompute and refresh.

        Args:
            obj: An object with reactive attributes.
            value: the value to set the reactive attribute to.
        """
        _rich_traceback_omit = True

        self._set_reactive_inner(obj, value)

        if self._trigger_object_compute:
            self._compute_reactable_object(obj)

        # Refresh according to descriptor flags
        if self._layout or self._repaint:
            obj.refresh(repaint=self._repaint, layout=self._layout)

    def _set_reactive_inner(self, obj: Reactable, value: ReactiveType) -> None:
        """Set the value of the reactive attribute, invoking any
        validation and watch methods.

        Does _not_ invoke object-wide recompute nor refresh.

        Args:
            obj: An object with reactive attributes.
            value: the value to set the reactive attribute to.
        """
        _rich_traceback_omit = True

        self._initialize_reactive(obj)

        # Call validate function
        validate_function = self.validate_function
        if callable(validate_function):
            value = validate_function(obj, value)

        current_value = self.__get__(obj)
        if current_value == value and not self._always_update:
            return

        # Store the internal value
        setattr(obj, self.internal_name, value)

        # Notify all watchers
        self._notify_reactive_watchers(obj, current_value)

    def _compute_reactive(self, obj: Reactable) -> None:
        """Compute the value of the reactive attribute,
        storing it the reactive cache (which itself invokes
        any validation and watch methods).

        Does _not_ invoke object-wide recompute nor refresh.

        Args:
            obj: An object with reactive attributes.
        """
        _rich_traceback_omit = True

        compute_method = self.compute_function
        if compute_method is None:
            return
        value = compute_method(obj)

        self._set_reactive_inner(obj, value)

    def _initialize_reactive(self, obj: Reactable) -> None:
        """Initialize the reactive attribute on an object.

        Args:
            obj: An object with reactive attributes.
        """
        internal_name = self.internal_name
        if hasattr(obj, internal_name):
            # Attribute already has a value
            return
        compute_function = self.compute_function
        if compute_function is not None and self._init:
            default = compute_function(obj)
        else:
            default_or_callable = self._default
            default = (
                default_or_callable()
                if callable(default_or_callable)
                else default_or_callable
            )
        setattr(obj, internal_name, default)
        if self._init:
            self._notify_reactive_watchers(obj, default)

    def _notify_reactive_watchers(self, obj: Reactable, old_value: Any) -> None:
        """Notify all watchers

        Args:
            obj: The reactable object.
            old_value: The old (previous) value of the attribute.
        """
        _rich_traceback_omit = True

        async def await_watcher(awaitable: Awaitable) -> None:
            """Coroutine to await an awaitable returned from a watcher"""
            _rich_traceback_omit = True
            await awaitable

        def invoke_watcher(
            watch_function: Callable, old_value: object, value: object
        ) -> None:
            """Invoke a watch function.

            Args:
                watch_function: A watch function, which may be sync or async.
                old_value: The old value of the attribute.
                value: The new value of the attribute.
            """
            _rich_traceback_omit = True
            param_count = count_parameters(watch_function)
            if param_count == 2:
                watch_result = watch_function(old_value, value)
            elif param_count == 1:
                watch_result = watch_function(value)
            else:
                watch_result = watch_function()
            if isawaitable(watch_result):
                # Result is awaitable, so we need to await it within an async context
                obj.post_message_no_wait(
                    events.Callback(
                        sender=obj, callback=partial(await_watcher, watch_result)
                    )
                )

        # Get the current value.
        value = self.__get__(obj)

        watch_function = self.watch_function
        if callable(watch_function):
            invoke_watcher(partial(watch_function, obj), old_value, value)

        watchers: list[Callable] = getattr(obj, "__watchers", {}).get(self.name, [])
        for watcher in watchers:
            invoke_watcher(watcher, old_value, value)

    ##
    ## ONCE PER `Reactable` OBJECT INSTANCE
    ##

    @classmethod
    def _initialize_reactable_object(cls, obj: Reactable) -> None:
        """Set defaults and call any watchers / computes for the first time.

        Args:
            obj: An object with Reactive descriptors
        """
        _rich_traceback_guard = True
        for reactive in obj._reactives.values():
            reactive._initialize_reactive(obj)

    @classmethod
    def _reset_reactable_object(cls, obj: Reactable) -> None:
        """Reset reactive structures on object (to avoid reference cycles).

        Args:
            obj: A reactive object.
        """
        _rich_traceback_guard = True
        getattr(obj, "__watchers", {}).clear()

    @classmethod
    def _compute_reactable_object(cls, obj: Reactable) -> None:
        """Invoke all computes.

        Args:
            obj: Reactable object.
        """
        _rich_traceback_guard = True
        for reactive in obj._reactives.values():
            reactive._compute_reactive(obj)


class reactive(Reactive[ReactiveType]):
    """Create a reactive attribute.

    Args:
        default: A default value or callable that returns a default.
        layout: Perform a layout on change. Defaults to False.
        repaint: Perform a repaint on change. Defaults to True.
        init: Call watchers on initialize (post mount). Defaults to True.
        always_update: Call watchers even when the new value equals the old value. Defaults to False.
    """

    def __init__(
        self,
        default: ReactiveType | Callable[[], ReactiveType],
        *,
        layout: bool = False,
        repaint: bool = True,
        init: bool = True,
        always_update: bool = False,
    ) -> None:
        super().__init__(
            default,
            layout=layout,
            repaint=repaint,
            init=init,
            always_update=always_update,
        )


class var(Reactive[ReactiveType]):
    """Create a reactive attribute (with no auto-refresh).

    Args:
        default: A default value or callable that returns a default.
        init: Call watchers on initialize (post mount). Defaults to True.
    """

    def __init__(
        self,
        default: ReactiveType | Callable[[], ReactiveType],
        init: bool = True,
    ) -> None:
        super().__init__(
            default,
            layout=False,
            repaint=False,
            init=init,
        )


class init(Reactive[ReactiveType]):
    def init(
        self,
        default: ReactiveType | Callable[[], ReactiveType],
        *,
        layout: bool = False,
        repaint: bool = True,
        always_update: bool = False,
        compute: bool = True,
    ) -> None:
        """A reactive variable that calls watchers and compute on initialize (post mount).

        Args:
            default: A default value or callable that returns a default.
            layout: Perform a layout on change. Defaults to False.
            repaint: Perform a repaint on change. Defaults to True.
            always_update: Call watchers even when the new value equals the old value. Defaults to False.
            compute: Run compute methods when attribute is changed. Defaults to True.
        """
        super().__init__(
            default,
            layout=layout,
            repaint=repaint,
            init=True,
            always_update=always_update,
            compute=compute,
        )


def watch(
    obj: Reactable,
    attribute_name: str,
    callback: Callable[[Any], object],
    init: bool = True,
) -> None:
    """Watch a reactive variable on an object.

    Args:
        obj: The parent object.
        attribute_name: The attribute to watch.
        callback: A callable to call when the attribute changes.
        init: True to call watcher initialization. Defaults to True.
    """

    if not hasattr(obj, "__watchers"):
        setattr(obj, "__watchers", {})
    watchers: dict[str, list[Callable]] = getattr(obj, "__watchers")
    watcher_list = watchers.setdefault(attribute_name, [])
    if callback in watcher_list:
        return
    watcher_list.append(callback)
    if init:
        reactive = obj._reactives[attribute_name]
        current_value = reactive.__get__(obj)
        reactive._notify_reactive_watchers(obj, current_value)
