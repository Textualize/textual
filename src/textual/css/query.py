"""
This module contains the `DOMQuery` class and related objects.

A DOMQuery is a set of DOM nodes returned by [query][textual.dom.DOMNode.query].

The set of nodes may be further refined with [filter][textual.css.query.DOMQuery.filter] and [exclude][textual.css.query.DOMQuery.exclude].
Additional methods apply actions to all nodes in the query.

!!! info

    If this sounds like JQuery, a (once) popular JS library, it is no coincidence.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Iterable, Iterator, TypeVar, cast, overload

import rich.repr

from textual._context import active_app
from textual.await_remove import AwaitRemove
from textual.css.errors import DeclarationError, TokenError
from textual.css.match import match
from textual.css.model import SelectorSet
from textual.css.parse import parse_declarations, parse_selectors

if TYPE_CHECKING:
    from textual.dom import DOMNode
    from textual.widget import Widget


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
"""Type variable used to type generic queries."""
ExpectType = TypeVar("ExpectType")
"""Type variable used to further restrict queries."""


@rich.repr.auto(angular=True)
class DOMQuery(Generic[QueryType]):
    __slots__ = ["_node", "_nodes", "_filters", "_excludes", "_deep"]

    def __init__(
        self,
        node: DOMNode,
        *,
        filter: str | None = None,
        exclude: str | None = None,
        deep: bool = True,
        parent: DOMQuery | None = None,
    ) -> None:
        """Initialize a query object.

        !!! warning

            You won't need to construct this manually, as `DOMQuery` objects are returned by [query][textual.dom.DOMNode.query].

        Args:
            node: A DOM node.
            filter: Query to filter children in the node.
            exclude: Query to exclude children in the node.
            deep: Query should be deep, i.e. recursive.
            parent: The parent query, if this is the result of filtering another query.

        Raises:
            InvalidQueryFormat: If the format of the query is invalid.
        """
        _rich_traceback_omit = True
        self._node = node
        self._nodes: list[QueryType] | None = None
        self._filters: list[tuple[SelectorSet, ...]] = (
            parent._filters.copy() if parent else []
        )
        self._excludes: list[tuple[SelectorSet, ...]] = (
            parent._excludes.copy() if parent else []
        )
        self._deep = deep
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
        """The node being queried."""
        return self._node

    @property
    def nodes(self) -> list[QueryType]:
        """Lazily evaluate nodes."""
        from textual.widget import Widget

        if self._nodes is None:
            initial_nodes = list(
                self._node.walk_children(Widget) if self._deep else self._node._nodes
            )
            nodes = [
                node
                for node in initial_nodes
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

    if TYPE_CHECKING:

        @overload
        def __getitem__(self, index: int) -> QueryType: ...

        @overload
        def __getitem__(self, index: slice) -> list[QueryType]: ...

    def __getitem__(self, index: int | slice) -> QueryType | list[QueryType]:
        return self.nodes[index]

    def __rich_repr__(self) -> rich.repr.Result:
        try:
            if self._filters:
                yield (
                    "query",
                    " AND ".join(
                        ",".join(selector.css for selector in selectors)
                        for selectors in self._filters
                    ),
                )
            if self._excludes:
                yield (
                    "exclude",
                    " OR ".join(
                        ",".join(selector.css for selector in selectors)
                        for selectors in self._excludes
                    ),
                )
        except AttributeError:
            pass

    def filter(self, selector: str) -> DOMQuery[QueryType]:
        """Filter this set by the given CSS selector.

        Args:
            selector: A CSS selector.

        Returns:
            New DOM Query.
        """

        return DOMQuery(
            self.node,
            filter=selector,
            deep=self._deep,
            parent=self,
        )

    def exclude(self, selector: str) -> DOMQuery[QueryType]:
        """Exclude nodes that match a given selector.

        Args:
            selector: A CSS selector.

        Returns:
            New DOM query.
        """
        return DOMQuery(
            self.node,
            exclude=selector,
            deep=self._deep,
            parent=self,
        )

    if TYPE_CHECKING:

        @overload
        def first(self) -> QueryType: ...

        @overload
        def first(self, expect_type: type[ExpectType]) -> ExpectType: ...

    def first(
        self, expect_type: type[ExpectType] | None = None
    ) -> QueryType | ExpectType:
        """Get the *first* matching node.

        Args:
            expect_type: Require matched node is of this type,
                or None for any type.

        Raises:
            WrongType: If the wrong type was found.
            NoMatches: If there are no matching nodes in the query.

        Returns:
            The matching Widget.
        """
        _rich_traceback_omit = True
        if self.nodes:
            first = self.nodes[0]
            if expect_type is not None:
                if not isinstance(first, expect_type):
                    raise WrongType(
                        f"Query value is wrong type; expected {expect_type}, got {type(first)}"
                    )
            return first
        else:
            raise NoMatches(f"No nodes match {self!r} on {self.node!r}")

    if TYPE_CHECKING:

        @overload
        def only_one(self) -> QueryType: ...

        @overload
        def only_one(self, expect_type: type[ExpectType]) -> ExpectType: ...

    def only_one(
        self, expect_type: type[ExpectType] | None = None
    ) -> QueryType | ExpectType:
        """Get the *only* matching node.

        Args:
            expect_type: Require matched node is of this type,
                or None for any type.

        Raises:
            WrongType: If the wrong type was found.
            NoMatches: If no node matches the query.
            TooManyMatches: If there is more than one matching node in the query.

        Returns:
            The matching Widget.
        """
        _rich_traceback_omit = True
        # Call on first to get the first item. Here we'll use all of the
        # testing and checking it provides.
        the_one: ExpectType | QueryType = (
            self.first(expect_type) if expect_type is not None else self.first()
        )
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
        return the_one

    if TYPE_CHECKING:

        @overload
        def last(self) -> QueryType: ...

        @overload
        def last(self, expect_type: type[ExpectType]) -> ExpectType: ...

    def last(
        self, expect_type: type[ExpectType] | None = None
    ) -> QueryType | ExpectType:
        """Get the *last* matching node.

        Args:
            expect_type: Require matched node is of this type,
                or None for any type.

        Raises:
            WrongType: If the wrong type was found.
            NoMatches: If there are no matching nodes in the query.

        Returns:
            The matching Widget.
        """
        if not self.nodes:
            raise NoMatches(f"No nodes match {self!r} on dom{self.node!r}")
        last = self.nodes[-1]
        if expect_type is not None and not isinstance(last, expect_type):
            raise WrongType(
                f"Query value is wrong type; expected {expect_type}, got {type(last)}"
            )
        return last

    if TYPE_CHECKING:

        @overload
        def results(self) -> Iterator[QueryType]: ...

        @overload
        def results(self, filter_type: type[ExpectType]) -> Iterator[ExpectType]: ...

    def results(
        self, filter_type: type[ExpectType] | None = None
    ) -> Iterator[QueryType | ExpectType]:
        """Get query results, optionally filtered by a given type.

        Args:
            filter_type: A Widget class to filter results,
                or None for no filter.

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

    def set_classes(self, classes: str | Iterable[str]) -> DOMQuery[QueryType]:
        """Set the classes on nodes to exactly the given set.

        Args:
            classes: A string of space separated classes, or an iterable of class names.

        Returns:
            Self.
        """

        if isinstance(classes, str):
            for node in self:
                node.set_classes(classes)
        else:
            class_names = list(classes)
            for node in self:
                node.set_classes(class_names)
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
        return app._prune(*self.nodes, parent=self._node)

    def set_styles(
        self, css: str | None = None, **update_styles
    ) -> DOMQuery[QueryType]:
        """Set styles on matched nodes.

        Args:
            css: CSS declarations to parser, or None.
        """
        _rich_traceback_omit = True

        for node in self:
            node.set_styles(**update_styles)
        if css is not None:
            try:
                new_styles = parse_declarations(css, read_from=("set_styles", ""))
            except DeclarationError as error:
                raise DeclarationError(error.name, error.token, error.message) from None
            for node in self:
                node._inline_styles.merge(new_styles)
                node.refresh(layout=True)
        return self

    def refresh(
        self, *, repaint: bool = True, layout: bool = False, recompose: bool = False
    ) -> DOMQuery[QueryType]:
        """Refresh matched nodes.

        Args:
            repaint: Repaint node(s).
            layout: Layout node(s).
            recompose: Recompose node(s).

        Returns:
            Query for chaining.
        """
        for node in self:
            node.refresh(repaint=repaint, layout=layout, recompose=recompose)
        return self

    def focus(self) -> DOMQuery[QueryType]:
        """Focus the first matching node that permits focus.

        Returns:
            Query for chaining.
        """
        for node in self:
            if node.allow_focus():
                node.focus()
                break
        return self

    def blur(self) -> DOMQuery[QueryType]:
        """Blur the first matching node that is focused.

        Returns:
            Query for chaining.
        """
        focused = self._node.screen.focused
        if focused is not None:
            nodes: list[Widget] = list(self)
            if focused in nodes:
                self._node.screen._reset_focus(focused, avoiding=nodes)
        return self

    def set(
        self,
        display: bool | None = None,
        visible: bool | None = None,
        disabled: bool | None = None,
        loading: bool | None = None,
    ) -> DOMQuery[QueryType]:
        """Sets common attributes on matched nodes.

        Args:
            display: Set `display` attribute on nodes, or `None` for no change.
            visible: Set `visible` attribute on nodes, or `None` for no change.
            disabled: Set `disabled` attribute on nodes, or `None` for no change.
            loading: Set `loading` attribute on nodes, or `None` for no change.

        Returns:
            Query for chaining.
        """
        for node in self:
            if display is not None:
                node.display = display
            if visible is not None:
                node.visible = visible
            if disabled is not None:
                node.disabled = disabled
            if loading is not None:
                node.loading = loading
        return self
