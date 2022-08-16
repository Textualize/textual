"""
A DOMQuery is a set of DOM nodes associated with a given CSS selector.

This set of nodes may be further filtered with the filter method. Additional methods apply
actions to the nodes in the query.

If this sounds like JQuery, a (once) popular JS library, it is no coincidence.

DOMQuery objects are typically created by Widget.query method.

Queries are *lazy*. Results will be calculated at the point you iterate over the query, or call
a method which evaluates the query, such as first() and last().

"""


from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, TypeVar, overload

import rich.repr

from .errors import DeclarationError
from .match import match
from .model import SelectorSet
from .parse import parse_declarations, parse_selectors

if TYPE_CHECKING:
    from ..dom import DOMNode
    from ..widget import Widget


class QueryError(Exception):
    pass


class NoMatchingNodesError(QueryError):
    pass


class WrongType(QueryError):
    pass


@rich.repr.auto(angular=True)
class DOMQuery:
    __slots__ = [
        "_node",
        "_nodes",
        "_filters",
        "_excludes",
    ]

    def __init__(
        self,
        node: DOMNode,
        *,
        filter: str | None = None,
        exclude: str | None = None,
        parent: DOMQuery | None = None,
    ) -> None:

        self._node = node
        self._nodes: list[Widget] | None = None
        self._filters: list[tuple[SelectorSet, ...]] = (
            parent._filters.copy() if parent else []
        )
        self._excludes: list[tuple[SelectorSet, ...]] = (
            parent._excludes.copy() if parent else []
        )
        if filter is not None:
            self._filters.append(parse_selectors(filter))
        if exclude is not None:
            self._excludes.append(parse_selectors(exclude))

    @property
    def node(self) -> DOMNode:
        return self._node

    @property
    def nodes(self) -> list[Widget]:
        """Lazily evaluate nodes."""
        from ..widget import Widget

        if self._nodes is None:
            nodes = [
                node
                for node in self._node.walk_children(Widget)
                if all(match(selector_set, node) for selector_set in self._filters)
            ]
            nodes = [
                node
                for node in nodes
                if not any(match(selector_set, node) for selector_set in self._excludes)
            ]
            self._nodes = nodes
        return self._nodes

    def __len__(self) -> int:
        return len(self.nodes)

    def __bool__(self) -> bool:
        """True if non-empty, otherwise False."""
        return bool(self.nodes)

    def __iter__(self) -> Iterator[Widget]:
        return iter(self.nodes)

    def __reversed__(self) -> Iterator[Widget]:
        return reversed(self.nodes)

    @overload
    def __getitem__(self, index: int) -> Widget:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[Widget]:
        ...

    def __getitem__(self, index: int | slice) -> Widget | list[Widget]:
        return self.nodes[index]

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.node
        if self._filters:
            yield "filter", " AND ".join(
                ",".join(selector.css for selector in selectors)
                for selectors in self._filters
            )
        if self._excludes:
            yield "exclude", " OR ".join(
                ",".join(selector.css for selector in selectors)
                for selectors in self._excludes
            )

    def filter(self, selector: str) -> DOMQuery:
        """Filter this set by the given CSS selector.

        Args:
            selector (str): A CSS selector.

        Returns:
            DOMQuery: New DOM Query.
        """

        return DOMQuery(self.node, filter=selector, parent=self)

    def exclude(self, selector: str) -> DOMQuery:
        """Exclude nodes that match a given selector.

        Args:
            selector (str): A CSS selector.

        Returns:
            DOMQuery: New DOM query.
        """
        return DOMQuery(self.node, exclude=selector, parent=self)

    ExpectType = TypeVar("ExpectType")

    @overload
    def first(self) -> Widget:
        ...

    @overload
    def first(self, expect_type: type[ExpectType]) -> ExpectType:
        ...

    def first(self, expect_type: type[ExpectType] | None = None) -> Widget | ExpectType:
        """Get the *first* match node.

        Args:
            expect_type (type[ExpectType] | None, optional): Require matched node is of this type,
                or None for any type. Defaults to None.

        Raises:
            WrongType: If the wrong type was found.
            NoMatchingNodesError: If there are no matching nodes in the query.

        Returns:
            Widget | ExpectType: The matching Widget.
        """
        if self.nodes:
            first = self.nodes[0]
            if expect_type is not None:
                if not isinstance(first, expect_type):
                    raise WrongType(
                        f"Query value is wrong type; expected {expect_type}, got {type(first)}"
                    )
            return first
        else:
            raise NoMatchingNodesError(f"No nodes match {self!r}")

    @overload
    def last(self) -> Widget:
        ...

    @overload
    def last(self, expect_type: type[ExpectType]) -> ExpectType:
        ...

    def last(self, expect_type: type[ExpectType] | None = None) -> Widget | ExpectType:
        """Get the *last* match node.

        Args:
            expect_type (type[ExpectType] | None, optional): Require matched node is of this type,
                or None for any type. Defaults to None.

        Raises:
            WrongType: If the wrong type was found.
            NoMatchingNodesError: If there are no matching nodes in the query.

        Returns:
            Widget | ExpectType: The matching Widget.
        """
        if self.nodes:
            last = self.nodes[-1]
            if expect_type is not None:
                if not isinstance(last, expect_type):
                    raise WrongType(
                        f"Query value is wrong type; expected {expect_type}, got {type(last)}"
                    )
            return last
        else:
            raise NoMatchingNodesError(f"No nodes match {self!r}")

    @overload
    def results(self) -> Iterator[Widget]:
        ...

    @overload
    def results(self, filter_type: type[ExpectType]) -> Iterator[ExpectType]:
        ...

    def results(
        self, filter_type: type[ExpectType] | None = None
    ) -> Iterator[Widget | ExpectType]:
        """Get query results, optionally filtered by a given type.

        Args:
            filter_type (type[ExpectType] | None): A Widget class to filter results,
                or None for no filter. Defaults to None.

        Yields:
            Iterator[Widget | ExpectType]: An iterator of Widget instances.
        """
        if filter_type is None:
            yield from self
        else:
            for node in self:
                if isinstance(node, filter_type):
                    yield node

    def add_class(self, *class_names: str) -> DOMQuery:
        """Add the given class name(s) to nodes."""
        for node in self:
            node.add_class(*class_names)
        return self

    def remove_class(self, *class_names: str) -> DOMQuery:
        """Remove the given class names from the nodes."""
        for node in self:
            node.remove_class(*class_names)
        return self

    def toggle_class(self, *class_names: str) -> DOMQuery:
        """Toggle the given class names from matched nodes."""
        for node in self:
            node.toggle_class(*class_names)
        return self

    def remove(self) -> DOMQuery:
        """Remove matched nodes from the DOM"""
        for node in self:
            node.remove()
        return self

    def set_styles(self, css: str | None = None, **update_styles) -> DOMQuery:
        """Set styles on matched nodes.

        Args:
            css (str, optional): CSS declarations to parser, or None. Defaults to None.
        """
        _rich_traceback_omit = True

        for node in self:
            node.set_styles(**update_styles)
        if css is not None:
            try:
                new_styles = parse_declarations(css, path="set_styles")
            except DeclarationError as error:
                raise DeclarationError(error.name, error.token, error.message) from None
            for node in self:
                node._inline_styles.merge(new_styles)
                node.refresh(layout=True)
        return self

    def refresh(self, *, repaint: bool = True, layout: bool = False) -> DOMQuery:
        """Refresh matched nodes.

        Args:
            repaint (bool): Repaint node(s). defaults to True.
            layout (bool): Layout node(s). Defaults to False.

        Returns:
            DOMQuery: Query for chaining.
        """
        for node in self:
            node.refresh(repaint=repaint, layout=layout)
        return self
