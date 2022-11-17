from __future__ import annotations
from importlib import import_module
import typing

from ..case import camel_to_snake

# ⚠️For any new built-in Widget we create, not only do we have to import them here and add them to `__all__`,
# but also to the `__init__.pyi` file in this same folder - otherwise text editors and type checkers won't
# be able to "see" them.
if typing.TYPE_CHECKING:
    from ..widget import Widget
    from ._button import Button
    from ._checkbox import Checkbox
    from ._data_table import DataTable
    from ._directory_tree import DirectoryTree
    from ._footer import Footer
    from ._header import Header
    from ._placeholder import Placeholder
    from ._pretty import Pretty
    from ._static import Static
    from ._input import Input
    from ._text_log import TextLog
    from ._tree_control import TreeControl
    from ._welcome import Welcome

__all__ = [
    "Button",
    "Checkbox",
    "DataTable",
    "DirectoryTree",
    "Footer",
    "Header",
    "Placeholder",
    "Pretty",
    "Static",
    "Input",
    "TextLog",
    "TreeControl",
    "Welcome",
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
