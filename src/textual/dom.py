from __future__ import annotations

import rich.repr

from .css.styles import Styles
from .message_pump import MessagePump
from ._node_list import NodeList


@rich.repr.auto
class DOMNode(MessagePump):
    """A node in a hierarchy of things forming the UI.

    Nodes are mountable and may be styled with CSS.

    """

    def __init__(self, name: str | None = None, id: str | None = None) -> None:
        self._name = name
        self._id = id
        self._classes: set[str] = set()
        self.children = NodeList()
        self.styles: Styles = Styles()
        super().__init__()

    def __rich_repr__(self) -> rich.repr.Result:
        yield "name", self._name, None
        yield "id", self._id, None
        if self._classes:
            yield "classes", self._classes

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def classes(self) -> frozenset[str]:
        return frozenset(self._classes)

    @property
    def css_type(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def css_path(self) -> list[tuple[DOMNode, list[DOMNode]]]:
        result: list[tuple[DOMNode, list[DOMNode]]] = []
        append = result.append

        node: DOMNode = self
        while isinstance(node._parent, DOMNode):
            append((node, node.children[:]))
            node = node._parent
        return result[::-1]

    def has_class(self, *class_names: str) -> bool:
        return self._classes.issuperset(class_names)

    def add_class(self, *class_names: str) -> None:
        """Add class names."""
        self._classes.update(class_names)

    def remove_class(self, *class_names: str) -> None:
        """Remove class names"""
        self._classes.difference_update(class_names)

    def toggle_class(self, *class_names: str) -> None:
        """Toggle class names"""
        self._classes.symmetric_difference_update(class_names)

    def has_psuedo_class(self, class_name: str) -> bool:
        """Check for psuedo class (such as hover, focus etc)"""
        classes = self.get_psuedo_classes()
        has_psuedo_class = class_name in classes
        return has_psuedo_class

    def get_psuedo_classes(self) -> set[str]:
        """Get a set of all psuedo classes"""
        return set()
