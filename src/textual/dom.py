from __future__ import annotations

import rich.repr

from .css.styles import Styles
from .message_pump import MessagePump
from ._node_list import NodeList


@rich.repr.auto
class DOMNode(MessagePump):
    def __init__(self, name: str | None = None, id: str | None = None) -> None:
        self._name = name
        self._id = id
        self._class_names: set[str] = set()
        self.children = NodeList()
        self.styles: Styles = Styles()
        super().__init__()

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def class_names(self) -> frozenset[str]:
        return frozenset(self._class_names)

    @property
    def css_type(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def css_path(self) -> list[tuple[DOMNode, list[DOMNode]]]:
        result: list[tuple[DOMNode, list[DOMNode]]] = []
        append = result.append

        # TODO:
        node: DOMNode = self
        while isinstance(node._parent, DOMNode):
            append((node, node.children[:]))
            node = node._parent
        return result[::-1]

    def has_class(self, *class_names: str) -> bool:
        return self._class_names.issuperset(class_names)

    def add_class(self, *class_names: str) -> None:
        """Add class names."""
        self._class_names.update(class_names)

    def remove_class(self, *class_names: str) -> None:
        """Remove class names"""
        self._class_names.difference_update(class_names)

    def toggle_class(self, *class_names: str) -> None:
        """Toggle class names"""
        self._class_names.symmetric_difference_update(class_names)
