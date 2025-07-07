from __future__ import annotations

"""
Descriptors to define properties on your widget, screen, or App.

"""

from typing import Generic, overload

from textual.css.query import QueryType
from textual.dom import DOMNode
from textual.widget import Widget


class query_one(Generic[QueryType]):
    """Create a query one property.

    A query one property calls [query_one][textual.dom.DOMNode.query_one] when accessed, and returns
    a widget.


    Example:
        ```python
        from textual import getters

        class MyScreen(screen):

            # Note this is at the class level
            output_log = getters.query_one("#output", RichLog)

            def compose(self) -> ComposeResult:
                yield RichLog(id="output")

            def on_mount(self) -> None:
                self.output_log.write("Screen started")
                # Equivalent to the following line:
                # self.query_one("#output", RichLog).write("Screen started")
        ```


    """

    selector: str
    expect_type: type[Widget]

    @overload
    def __init__(self, selector: str) -> None:
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
