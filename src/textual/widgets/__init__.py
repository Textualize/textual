from __future__ import annotations
from importlib import import_module
import typing

if typing.TYPE_CHECKING:
    from ..widget import Widget

# Let's decrease startup time by lazy loading our Widgets:
# ⚠ For any new built-in Widget we create, not only we have to add them to the following dictionary, but also to the
# `__init__.pyi` file in this same folder - otherwise text editors and type checkers won't be able to "see" them.
_WIDGETS_LAZY_LOADING_MAPPING: dict[str, str] = {
    "Footer": "._footer:Footer",
    "Header": "._header:Header",
    "Button": "._button:Button",
    "Placeholder": "._placeholder:Placeholder",
    "Static": "._static:Static",
    "TreeControl": "._tree_control:TreeControl",
    "TreeClick": "._tree_control:TreeClick",
    "TreeNode": "._tree_control:TreeNode",
    "NodeID": "._tree_control:NodeID",
    "DirectoryTree": "._directory_tree:DirectoryTree",
    "FileClick": "._directory_tree:FileClick",
}

_WIDGETS_LAZY_LOADING_CACHE: dict[str, type[Widget]] = {}


def __getattr__(widget_name: str) -> type[Widget]:
    try:
        return _WIDGETS_LAZY_LOADING_CACHE[widget_name]
    except KeyError:
        pass

    if widget_name not in _WIDGETS_LAZY_LOADING_MAPPING:
        raise ImportError(f"Widget {widget_name} not found")

    module_name, class_name = _WIDGETS_LAZY_LOADING_MAPPING[widget_name].split(":")
    module = import_module(module_name, package="textual.widgets")
    class_ = getattr(module, class_name)

    _WIDGETS_LAZY_LOADING_CACHE[widget_name] = class_
    return class_


__all__ = tuple(_WIDGETS_LAZY_LOADING_MAPPING.keys())
