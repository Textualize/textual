"""
A DOMQuery is a set of DOM nodes associated with a given CSS selector.

This set of nodes may be further filtered with the filter method. Additional methods apply
actions to the nodes in the query.

If this sounds like JQuery, a (once) popular JS library, it is no coincidence.

DOMQuery objects are typically created by Widget.filter method.

"""


from __future__ import annotations


import rich.repr

from typing import Iterator, TYPE_CHECKING


from .match import match
from .parse import parse_selectors

if TYPE_CHECKING:
    from ..dom import DOMNode


class NoMatchingNodesError(Exception):
    pass


@rich.repr.auto(angular=True)
class DOMQuery:
    def __init__(
        self,
        node: DOMNode | None = None,
        selector: str | None = None,
        nodes: list[DOMNode] | None = None,
    ) -> None:
        self._selector = selector
        self._nodes: list[DOMNode] = []
        if nodes is not None:
            self._nodes = nodes
        elif node is not None:
            self._nodes = list(node.walk_children())
        else:
            self._nodes = []

        if selector is not None:
            selector_set = parse_selectors(selector)
            self._nodes = [_node for _node in self._nodes if match(selector_set, _node)]

    def __len__(self) -> int:
        return len(self._nodes)

    def __bool__(self) -> bool:
        """True if non-empty, otherwise False."""
        return bool(self._nodes)

    def __iter__(self) -> Iterator[DOMNode]:
        return iter(self._nodes)

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._nodes

    def filter(self, selector: str) -> DOMQuery:
        """Filter this set by the given CSS selector.

        Args:
            selector (str): A CSS selector.

        Returns:
            DOMQuery: New DOM Query.
        """
        selector_set = parse_selectors(selector)
        query = DOMQuery(
            nodes=[_node for _node in self._nodes if match(selector_set, _node)]
        )
        return query

    def exclude(self, selector: str) -> DOMQuery:
        """Exclude nodes that match a given selector.

        Args:
            selector (str): A CSS selector.

        Returns:
            DOMQuery: New DOM query.
        """
        selector_set = parse_selectors(selector)
        query = DOMQuery(
            nodes=[_node for _node in self._nodes if not match(selector_set, _node)]
        )
        return query

    def first(self) -> DOMNode:
        """Get the first matched node.

        Returns:
            DOMNode: A DOM Node.
        """
        if self._nodes:
            return self._nodes[0]
        else:
            raise NoMatchingNodesError(
                f"No nodes match the selector {self._selector!r}"
            )

    def add_class(self, *class_names: str) -> DOMQuery:
        """Add the given class name(s) to nodes."""
        for node in self._nodes:
            node.add_class(*class_names)
        return self

    def remove_class(self, *class_names: str) -> DOMQuery:
        """Remove the given class names from the nodes."""
        for node in self._nodes:
            node.remove_class(*class_names)
        return self

    def toggle_class(self, *class_names: str) -> DOMQuery:
        """Toggle the given class names from matched nodes."""
        for node in self._nodes:
            node.toggle_class(*class_names)
        return self

    def set_styles(self, css: str | None = None, **styles: str) -> DOMQuery:
        """Set styles on matched nodes.

        Args:
            css (str, optional): CSS declarations to parser, or None. Defaults to None.
        """
        for node in self._nodes:
            node.set_styles(css, **styles)
        return self

    def refresh(self, repaint: bool = True, layout: bool = False) -> DOMQuery:
        """Refresh matched nodes.

        Args:
            repaint (bool): Repaint node(s). defaults to True.
            layout (bool): Layout node(s). Defaults to False.

        Returns:
            DOMQuery: Query for chaining.
        """
        for node in self._nodes:
            node.refresh(repaint=repaint, layout=layout)
        return self
