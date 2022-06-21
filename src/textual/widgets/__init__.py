from __future__ import annotations
from importlib import import_module
import typing

from ..case import camel_to_snake

if typing.TYPE_CHECKING:
    from ..widget import Widget


# ⚠️For any new built-in Widget we create, not only we have to add them to the following list, but also to the
# `__init__.pyi` file in this same folder - otherwise text editors and type checkers won't be able to "see" them.
__all__ = [
    "Button",
    "DataTable",
    "DirectoryTree",
    "Footer",
    "Header",
    "Placeholder",
    "Static",
    "TreeControl",
]


_WIDGETS_LAZY_LOADING_CACHE: dict[str, type[Widget]] = {}

# Let's decrease startup time by lazy loading our Widgets:
def __getattr__(widget_class: str) -> type[Widget]:
    try:
        return _WIDGETS_LAZY_LOADING_CACHE[widget_class]
    except KeyError:
        pass

    if widget_class not in __all__:
        raise ImportError(f"Package 'textual.widgets' has no class '{widget_class}'")

    widget_module_path = f"._{camel_to_snake(widget_class)}"
    module = import_module(widget_module_path, package="textual.widgets")
    class_ = getattr(module, widget_class)

    _WIDGETS_LAZY_LOADING_CACHE[widget_class] = class_
    return class_
