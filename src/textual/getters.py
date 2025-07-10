"""
Descriptors to define properties on your widget, screen, or App.

"""

from __future__ import annotations

from typing import Generic, overload

from textual.css.query import NoMatches, QueryType, WrongType
from textual.dom import DOMNode
from textual.widget import Widget


class query_one(Generic[QueryType]):
    """Create a query one property.

    A query one property calls [Widget.query_one][textual.dom.DOMNode.query_one] when accessed, and returns
    a widget. If the widget doesn't exist, then the property will raise the same exceptions as `Widget.query_one`.


    Example:
        ```python
        from textual import getters

        class MyScreen(screen):

            # Note this is at the class level
            output_log = getters.query_one("#output", RichLog)

            def compose(self) -> ComposeResult:
                with containers.Vertical():
                    yield RichLog(id="output")

            def on_mount(self) -> None:
                self.output_log.write("Screen started")
                # Equivalent to the following line:
                # self.query_one("#output", RichLog).write("Screen started")
        ```

    Args:
        selector: A TCSS selector, e.g. "#mywidget". Or a widget type, i.e. `Input`.
        expect_type: The type of the expected widget, e.g. `Input`, if the first argument is a selector.

    """

    selector: str
    expect_type: type[Widget]

    @overload
    def __init__(self, selector: str) -> None:
        """

        Args:
            selector: A TCSS selector, e.g. "#mywidget"
        """
        self.selector = selector
        self.expect_type = Widget

    @overload
    def __init__(self, selector: type[QueryType]) -> None:
        self.selector = selector.__name__
        self.expect_type = selector

    @overload
    def __init__(self, selector: str, expect_type: type[QueryType]) -> None:
        self.selector = selector
        self.expect_type = expect_type

    @overload
    def __init__(self, selector: type[QueryType], expect_type: type[QueryType]) -> None:
        self.selector = selector.__name__
        self.expect_type = expect_type

    def __init__(
        self,
        selector: str | type[QueryType],
        expect_type: type[QueryType] | None = None,
    ) -> None:
        if expect_type is None:
            self.expect_type = Widget
        else:
            self.expect_type = expect_type
        if isinstance(selector, str):
            self.selector = selector
        else:
            self.selector = selector.__name__
            self.expect_type = selector

    @overload
    def __get__(
        self: "query_one[QueryType]", obj: DOMNode, obj_type: type[DOMNode]
    ) -> QueryType: ...

    @overload
    def __get__(
        self: "query_one[QueryType]", obj: None, obj_type: type[DOMNode]
    ) -> "query_one[QueryType]": ...

    def __get__(
        self: "query_one[QueryType]", obj: DOMNode | None, obj_type: type[DOMNode]
    ) -> QueryType | Widget | "query_one":
        """Get the widget matching the selector and/or type."""
        if obj is None:
            return self
        query_node = obj.query_one(self.selector, self.expect_type)
        return query_node


class child_by_id(Generic[QueryType]):
    """Create a child_by_id property, which returns the child with the given ID.

    This is similar using [query_one][textual.getters.query_one] with an id selector, except that
    only the immediate children are considered. It is also more efficient as it doesn't need to search the DOM.


    Example:
        ```python
        from textual import getters

        class MyScreen(screen):

            # Note this is at the class level
            output_log = getters.child_by_id("output", RichLog)

            def compose(self) -> ComposeResult:
                yield RichLog(id="output")

            def on_mount(self) -> None:
                self.output_log.write("Screen started")
        ```

    Args:
        child_id: The `id` of the widget to get (not a selector).
        expect_type: The type of the expected widget, e.g. `Input`.

    """

    child_id: str
    expect_type: type[Widget]

    @overload
    def __init__(self, child_id: str) -> None:
        self.child_id = child_id
        self.expect_type = Widget

    @overload
    def __init__(self, child_id: str, expect_type: type[QueryType]) -> None:
        self.child_id = child_id
        self.expect_type = expect_type

    def __init__(
        self,
        child_id: str,
        expect_type: type[QueryType] | None = None,
    ) -> None:
        if expect_type is None:
            self.expect_type = Widget
        else:
            self.expect_type = expect_type
        self.child_id = child_id

    @overload
    def __get__(
        self: "child_by_id[QueryType]", obj: DOMNode, obj_type: type[DOMNode]
    ) -> QueryType: ...

    @overload
    def __get__(
        self: "child_by_id[QueryType]", obj: None, obj_type: type[DOMNode]
    ) -> "child_by_id[QueryType]": ...

    def __get__(
        self: "child_by_id[QueryType]", obj: DOMNode | None, obj_type: type[DOMNode]
    ) -> QueryType | Widget | "child_by_id":
        """Get the widget matching the selector and/or type."""
        if obj is None:
            return self
        child = obj._get_dom_base()._nodes._get_by_id(self.child_id)
        if child is None:
            raise NoMatches(f"No child found with id={self.child_id!r}")
        if not isinstance(child, self.expect_type):
            raise WrongType(
                f"Child with id={self.child_id!r} is the wrong type; expected type {self.expect_type.__name__!r}, found {child}"
            )
        return child
