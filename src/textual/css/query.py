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

from typing import TYPE_CHECKING, Generic, Iterator, TypeVar, cast, overload

import rich.repr

from .._context import active_app
from ..await_remove import AwaitRemove
from .errors import DeclarationError, TokenError
from .match import match
from .model import SelectorSet
from .parse import parse_declarations, parse_selectors

if TYPE_CHECKING:
    from ..dom import DOMNode
    from ..widget import Widget


class QueryError(Exception):
    """Base class for a query related error."""


class InvalidQueryFormat(QueryError):
    """Query did not parse correctly."""


class NoMatches(QueryError):
    """No nodes matched the query."""


class TooManyMatches(QueryError):
    """Too many nodes matched the query."""


class WrongType(QueryError):
    """Query result was not of the correct type."""


QueryType = TypeVar("QueryType", bound="Widget")


@rich.repr.auto(angular=True)
class DOMQuery(Generic[QueryType]):
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
        self._nodes: list[QueryType] | None = None
        self._filters: list[tuple[SelectorSet, ...]] = (
            parent._filters.copy() if parent else []
        )
        self._excludes: list[tuple[SelectorSet, ...]] = (
            parent._excludes.copy() if parent else []
        )
        if filter is not None:
            try:
                self._filters.append(parse_selectors(filter))
            except TokenError:
                # TODO: More helpful errors
                raise InvalidQueryFormat(f"Unable to parse filter {filter!r} as query")

        if exclude is not None:
            try:
                self._excludes.append(parse_selectors(exclude))
            except TokenError:
                raise InvalidQueryFormat(f"Unable to parse filter {filter!r} as query")

    @property
    def node(self) -> DOMNode:
        return self._node

    @property
    def nodes(self) -> list[QueryType]:
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
            self._nodes = cast("list[QueryType]", nodes)
        return self._nodes

    def __len__(self) -> int:
        return len(self.nodes)

    def __bool__(self) -> bool:
        """True if non-empty, otherwise False."""
        return bool(self.nodes)

    def __iter__(self) -> Iterator[QueryType]:
        return iter(self.nodes)

    def __reversed__(self) -> Iterator[QueryType]:
        return reversed(self.nodes)

    @overload
    def __getitem__(self, index: int) -> QueryType:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[QueryType]:
        ...

    def __getitem__(self, index: int | slice) -> QueryType | list[QueryType]:
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

    def filter(self, selector: str) -> DOMQuery[QueryType]:
        """Filter this set by the given CSS selector.

        Args:
            selector: A CSS selector.

        Returns:
            New DOM Query.
        """

        return DOMQuery(self.node, filter=selector, parent=self)

    def exclude(self, selector: str) -> DOMQuery[QueryType]:
        """Exclude nodes that match a given selector.

        Args:
            selector: A CSS selector.

        Returns:
            New DOM query.
        """
        return DOMQuery(self.node, exclude=selector, parent=self)

    ExpectType = TypeVar("ExpectType")

    @overload
    def first(self) -> Widget:
        ...

    @overload
    def first(self, expect_type: type[ExpectType]) -> ExpectType:
        ...

    def first(
        self, expect_type: type[ExpectType] | None = None
    ) -> QueryType | ExpectType:
        """Get the *first* matching node.

        Args:
            expect_type: Require matched node is of this type,
                or None for any type. Defaults to None.

        Raises:
            WrongType: If the wrong type was found.
            NoMatches: If there are no matching nodes in the query.

        Returns:
            The matching Widget.
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
            raise NoMatches(f"No nodes match {self!r}")

    @overload
    def only_one(self) -> Widget:
        ...

    @overload
    def only_one(self, expect_type: type[ExpectType]) -> ExpectType:
        ...

    def only_one(
        self, expect_type: type[ExpectType] | None = None
    ) -> Widget | ExpectType:
        """Get the *only* matching node.

        Args:
            expect_type: Require matched node is of this type,
                or None for any type. Defaults to None.

        Raises:
            WrongType: If the wrong type was found.
            NoMatches: If no node matches the query.
            TooManyMatches: If there is more than one matching node in the query.

        Returns:
            The matching Widget.
        """
        # Call on first to get the first item. Here we'll use all of the
        # testing and checking it provides.
        the_one = self.first(expect_type) if expect_type is not None else self.first()
        try:
            # Now see if we can access a subsequent item in the nodes. There
            # should *not* be anything there, so we *should* get an
            # IndexError. We *could* have just checked the length of the
            # query, but the idea here is to do the check as cheaply as
            # possible. "There can be only one!" -- Kurgan et al.
            _ = self.nodes[1]
            raise TooManyMatches(
                "Call to only_one resulted in more than one matched node"
            )
        except IndexError:
            # The IndexError was got, that's a good thing in this case. So
            # we return what we found.
            pass
        return cast("Widget", the_one)

    @overload
    def last(self) -> Widget:
        ...

    @overload
    def last(self, expect_type: type[ExpectType]) -> ExpectType:
        ...

    def last(
        self, expect_type: type[ExpectType] | None = None
    ) -> QueryType | ExpectType:
        """Get the *last* matching node.

        Args:
            expect_type: Require matched node is of this type,
                or None for any type. Defaults to None.

        Raises:
            WrongType: If the wrong type was found.
            NoMatches: If there are no matching nodes in the query.

        Returns:
            The matching Widget.
        """
        if not self.nodes:
            raise NoMatches(f"No nodes match {self!r}")
        last = self.nodes[-1]
        if expect_type is not None and not isinstance(last, expect_type):
            raise WrongType(
                f"Query value is wrong type; expected {expect_type}, got {type(last)}"
            )
        return last

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
            filter_type: A Widget class to filter results,
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

    def set_class(self, add: bool, *class_names: str) -> DOMQuery[QueryType]:
        """Set the given class name(s) according to a condition.

        Args:
            add: Add the classes if True, otherwise remove them.

        Returns:
            Self.
        """
        for node in self:
            node.set_class(add, *class_names)
        return self

    def add_class(self, *class_names: str) -> DOMQuery[QueryType]:
        """Add the given class name(s) to nodes."""
        for node in self:
            node.add_class(*class_names)
        return self

    def remove_class(self, *class_names: str) -> DOMQuery[QueryType]:
        """Remove the given class names from the nodes."""
        for node in self:
            node.remove_class(*class_names)
        return self

    def toggle_class(self, *class_names: str) -> DOMQuery[QueryType]:
        """Toggle the given class names from matched nodes."""
        for node in self:
            node.toggle_class(*class_names)
        return self

    def remove(self) -> AwaitRemove:
        """Remove matched nodes from the DOM.

        Returns:
            An awaitable object that waits for the widgets to be removed.
        """
        app = active_app.get()
        await_remove = app._remove_nodes(list(self), self._node)
        return await_remove

    def set_styles(
        self, css: str | None = None, **update_styles
    ) -> DOMQuery[QueryType]:
        """Set styles on matched nodes.

        Args:
            css: CSS declarations to parser, or None. Defaults to None.
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

    def refresh(
        self, *, repaint: bool = True, layout: bool = False
    ) -> DOMQuery[QueryType]:
        """Refresh matched nodes.

        Args:
            repaint: Repaint node(s). defaults to True.
            layout: Layout node(s). Defaults to False.

        Returns:
            Query for chaining.
        """
        for node in self:
            node.refresh(repaint=repaint, layout=layout)
        return self
