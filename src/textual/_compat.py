from __future__ import annotations

import sys
from typing import Any, Generic, TypeVar, overload

if sys.version_info >= (3, 12):
    from functools import cached_property
else:
    # based on the code from Python 3.14:
    # https://github.com/python/cpython/blob/
    # 5507eff19c757a908a2ff29dfe423e35595fda00/Lib/functools.py#L1089-L1138
    # Copyright (C) 2006 Python Software Foundation.
    # vendored under the PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2 because
    # prior to Python 3.12 cached_property used a threading.Lock, which makes
    # it very slow.
    _T_co = TypeVar("_T_co", covariant=True)
    _NOT_FOUND = object()

    class cached_property(Generic[_T_co]):
        def __init__(self, func: Callable[[Any, _T_co]]) -> None:
            self.func = func
            self.attrname = None
            self.__doc__ = func.__doc__
            self.__module__ = func.__module__

        def __set_name__(self, owner: type[any], name: str) -> None:
            if self.attrname is None:
                self.attrname = name
            elif name != self.attrname:
                raise TypeError(
                    "Cannot assign the same cached_property to two different names "
                    f"({self.attrname!r} and {name!r})."
                )

        @overload
        def __get__(self, instance: None, owner: type[Any] | None = None) -> Self: ...

        @overload
        def __get__(
            self, instance: object, owner: type[Any] | None = None
        ) -> _T_co: ...

        def __get__(
            self, instance: object, owner: type[Any] | None = None
        ) -> _T_co | Self:
            if instance is None:
                return self
            if self.attrname is None:
                raise TypeError(
                    "Cannot use cached_property instance without calling __set_name__ on it."
                )
            try:
                cache = instance.__dict__
            except (
                AttributeError
            ):  # not all objects have __dict__ (e.g. class defines slots)
                msg = (
                    f"No '__dict__' attribute on {type(instance).__name__!r} "
                    f"instance to cache {self.attrname!r} property."
                )
                raise TypeError(msg) from None
            val = cache.get(self.attrname, _NOT_FOUND)
            if val is _NOT_FOUND:
                val = self.func(instance)
                try:
                    cache[self.attrname] = val
                except TypeError:
                    msg = (
                        f"The '__dict__' attribute on {type(instance).__name__!r} instance "
                        f"does not support item assignment for caching {self.attrname!r} property."
                    )
                    raise TypeError(msg) from None
            return val
