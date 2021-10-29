from __future__ import annotations

from rich.highlighter import ReprHighlighter
import rich.repr
from rich.pretty import Pretty
from rich.tree import Tree

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
    def psuedo_classes(self) -> set[str]:
        """Get a set of all psuedo classes"""
        return set()

    @property
    def css_type(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def css_path(self) -> list[tuple[DOMNode, list[DOMNode]]]:
        result: list[tuple[DOMNode, list[DOMNode]]] = [(self, self.children[:])]
        append = result.append

        node: DOMNode = self
        while isinstance(node._parent, DOMNode):
            node = node._parent
            append((node, node.children[:]))
        return result[::-1]

    @property
    def tree(self) -> Tree:
        highlighter = ReprHighlighter()
        tree = Tree(highlighter(repr(self)))

        def add_children(tree, node):
            for child in node.children:
                branch = tree.add(Pretty(child))
                if tree.children:
                    add_children(branch, child)

        add_children(tree, self)
        return tree

    def add_child(self, node: DOMNode) -> None:
        self.children._append(node)
        node.set_parent(self)

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

    def has_psuedo_class(self, *class_names: str) -> bool:
        """Check for psuedo class (such as hover, focus etc)"""
        has_psuedo_classes = self.psuedo_classes.issuperset(class_names)
        return has_psuedo_classes
