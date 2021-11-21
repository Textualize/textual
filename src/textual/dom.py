from __future__ import annotations

from typing import cast, Iterable, Iterator, TYPE_CHECKING

from rich.highlighter import ReprHighlighter
import rich.repr
from rich.pretty import Pretty
from rich.tree import Tree

from .css.styles import Styles
from .message_pump import MessagePump
from ._node_list import NodeList


if TYPE_CHECKING:
    from .css.query import DOMQuery
    from .widget import Widget


class NoParent(Exception):
    pass


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
    def parent(self) -> DOMNode:
        if self._parent is None:
            raise NoParent(f"{self._parent} has no parent")
        assert isinstance(self._parent, DOMNode)
        return self._parent

    @property
    def id(self) -> str | None:
        return self._id

    @id.setter
    def id(self, new_id: str) -> str:
        if self._id is not None:
            raise ValueError(
                "Node 'id' attribute may not be changed once set (current id={self._id!r})"
            )
        self._id = new_id
        return new_id

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
    def css_path(self) -> list[DOMNode]:
        result: list[DOMNode] = [self]
        append = result.append

        node: DOMNode = self
        while isinstance(node._parent, DOMNode):
            node = node._parent
            append(node)
        return result[::-1]

    @property
    def visible(self) -> bool:
        return self.styles.display != "none"

    @property
    def z(self) -> tuple[int, ...]:
        """Get the z index tuple for this node.

        Returns:
            tuple[int, ...]: A tuple of ints to sort layers by.
        """
        indexes: list[int] = []
        append = indexes.append
        node = self
        while node._parent:
            styles = node.styles
            parent_styles = node.parent.styles
            append(
                parent_styles.layers.index(styles.layer)
                if styles.layer in parent_styles.layers
                else 0
            )
            node = node.parent
        return tuple(reversed(indexes))

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

    def walk_children(self, with_self: bool = True) -> Iterable[DOMNode]:

        stack: list[Iterator[DOMNode]] = [iter(self.children)]
        pop = stack.pop
        push = stack.append

        if with_self:
            yield self

        while stack:
            node = next(stack[-1], None)
            if node is None:
                pop()
            else:
                yield node
                if node.children:
                    push(iter(node.children))

    def query(self, selector: str) -> DOMQuery:
        from .css.query import DOMQuery

        return DOMQuery(self, selector)

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
