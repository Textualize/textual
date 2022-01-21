from __future__ import annotations

from typing import Iterable, Iterator, TYPE_CHECKING

import rich.repr
from rich.highlighter import ReprHighlighter
from rich.pretty import Pretty
from rich.style import Style
from rich.tree import Tree

from ._node_list import NodeList
from .css._error_tools import friendly_list
from .css.constants import VALID_DISPLAY
from .css.errors import StyleValueError
from .css.styles import Styles
from .message_pump import MessagePump

if TYPE_CHECKING:
    from .css.query import DOMQuery


class NoParent(Exception):
    pass


@rich.repr.auto
class DOMNode(MessagePump):
    """A node in a hierarchy of things forming the UI.

    Nodes are mountable and may be styled with CSS.

    """

    STYLES = ""

    def __init__(self, name: str | None = None, id: str | None = None) -> None:
        self._name = name
        self._id = id
        self._classes: set[str] = set()
        self.children = NodeList()
        self.styles: Styles = Styles(self)
        super().__init__()
        self.default_styles = Styles.parse(self.STYLES, repr(self))
        self._default_rules = self.default_styles.extract_rules((0, 0, 0))

    def __rich_repr__(self) -> rich.repr.Result:
        yield "name", self._name, None
        yield "id", self._id, None
        if self._classes:
            yield "classes", self._classes

    @property
    def parent(self) -> DOMNode:
        """Get the parent node.

        Raises:
            NoParent: If this is the root node.

        Returns:
            DOMNode: The node which is the direct parent of this node.
        """
        if self._parent is None:
            raise NoParent(f"{self} has no parent")
        assert isinstance(self._parent, DOMNode)
        return self._parent

    @property
    def id(self) -> str | None:
        """The ID of this node, or None if the node has no ID.

        Returns:
            (str | None): A Node ID or None.
        """
        return self._id

    @id.setter
    def id(self, new_id: str) -> str:
        """Sets the ID (may only be done once).

        Args:
            new_id (str): ID for this node.

        Raises:
            ValueError: If the ID has already been set.

        """
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
    def pseudo_classes(self) -> frozenset[str]:
        """Get a set of all pseudo classes"""
        pseudo_classes = frozenset({*self.get_pseudo_classes()})
        return pseudo_classes

    @property
    def css_type(self) -> str:
        """Gets the CSS type, used by the CSS.

        Returns:
            str: A type used in CSS (lower cased class name).
        """
        return self.__class__.__name__.lower()

    @property
    def css_path(self) -> list[DOMNode]:
        """A list of nodes from the root to this node, forming a "path".

        Returns:
            list[DOMNode]: List of Nodes, starting with the root and ending with this node.
        """
        result: list[DOMNode] = [self]
        append = result.append

        node: DOMNode = self
        while isinstance(node._parent, DOMNode):
            node = node._parent
            append(node)
        return result[::-1]

    @property
    def display(self) -> bool:
        """
        Returns: ``True`` if this DOMNode is displayed (``display != "none"``), ``False`` otherwise.
        """
        return self.styles.display != "none"

    @display.setter
    def display(self, new_val: bool | str) -> None:
        """
        Args:
            new_val (bool | str): Shortcut to set the ``display`` CSS property.
                ``False`` will set ``display: none``. ``True`` will set ``display: block``.
                A ``False`` value will prevent the DOMNode from consuming space in the layout.
        """
        # TODO: This will forget what the original "display" value was, so if a user
        #  toggles to False then True, we'll reset to the default "block", rather than
        #  what the user initially specified.
        if isinstance(new_val, bool):
            self.styles.display = "block" if new_val else "none"
        elif new_val in VALID_DISPLAY:
            self.styles.display = new_val
        else:
            raise StyleValueError(
                f"invalid value for display (received {new_val!r}, "
                f"expected {friendly_list(VALID_DISPLAY)})",
            )

    @property
    def z(self) -> tuple[int, ...]:
        """Get the z index tuple for this node.

        Returns:
            tuple[int, ...]: A tuple of ints to sort layers by.
        """
        indexes: list[int] = []
        append = indexes.append
        node = self
        layer: str = node.styles.layer
        while node._parent:
            parent_styles = node.parent.styles
            layer = layer or node.styles.layer
            if layer in parent_styles.layers:
                append(parent_styles.layers.index(layer))
                layer = ""
            else:
                append(0)
            node = node.parent
        return tuple(reversed(indexes))

    @property
    def text_style(self) -> Style:
        """Get the text style (added to parent style).

        Returns:
            Style: Rich Style object.
        """
        return (
            self.parent.text_style + self.styles.text
            if self.has_parent
            else self.styles.text
        )

    @property
    def tree(self) -> Tree:
        """Get a Rich tree object which will recursively render the structure of the node tree.

        Returns:
            Tree: A Rich object which may be printed.
        """
        highlighter = ReprHighlighter()
        tree = Tree(highlighter(repr(self)))

        def add_children(tree, node):
            for child in node.children:
                branch = tree.add(Pretty(child))
                if tree.children:
                    add_children(branch, child)

        add_children(tree, self)
        return tree

    def get_pseudo_classes(self) -> Iterable[str]:
        """Get any pseudo classes applicable to this Node, e.g. hover, focus.

        Returns:
            Iterable[str]: Iterable of strings, such as a generator.
        """
        return ()

    def reset_styles(self) -> None:
        from .widget import Widget

        for node in self.walk_children():
            node.styles = Styles(node=node)
            if isinstance(node, Widget):
                # node.clear_render_cache()
                node._repaint_required = True
                node._layout_required = True

    def on_style_change(self) -> None:
        pass

    def add_child(self, node: DOMNode) -> None:
        """Add a new child node.

        Args:
            node (DOMNode): A DOM node.
        """
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

    def query(self, selector: str | None = None) -> DOMQuery:
        """Get a DOM query.

        Args:
            selector (str, optional): A CSS selector or `None` for all nodes. Defaults to None.

        Returns:
            DOMQuery: A query object.
        """
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
        self.app.stylesheet.update(self.app)

    def has_pseudo_class(self, *class_names: str) -> bool:
        """Check for pseudo class (such as hover, focus etc)"""
        has_pseudo_classes = self.pseudo_classes.issuperset(class_names)
        return has_pseudo_classes
