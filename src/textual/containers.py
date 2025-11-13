"""
Container widgets for quick styling.

With the exception of `Center` and `Middle` containers will fill all of the space in the parent widget.

"""

from __future__ import annotations

from typing import ClassVar

from textual.binding import Binding, BindingType
from textual.layout import Layout
from textual.layouts.grid import GridLayout
from textual.reactive import reactive
from textual.widget import Widget


class Container(Widget):
    """Simple container widget, with vertical layout."""

    DEFAULT_CSS = """
    Container {
        width: 1fr;
        height: 1fr;
        layout: vertical;
        overflow: hidden hidden;
    }
    """


class ScrollableContainer(Widget, can_focus=True):
    """A scrollable container with vertical layout, and auto scrollbars on both axis."""

    # We don't typically want to maximize scrollable containers,
    # since the user can easily navigate the contents
    ALLOW_MAXIMIZE = False

    DEFAULT_CSS = """
    ScrollableContainer {
        width: 1fr;
        height: 1fr;
        layout: vertical;
        overflow: auto auto;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("up", "scroll_up", "Scroll Up", show=False),
        Binding("down", "scroll_down", "Scroll Down", show=False),
        Binding("left", "scroll_left", "Scroll Left", show=False),
        Binding("right", "scroll_right", "Scroll Right", show=False),
        Binding("home", "scroll_home", "Scroll Home", show=False),
        Binding("end", "scroll_end", "Scroll End", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
        Binding("ctrl+pageup", "page_left", "Page Left", show=False),
        Binding("ctrl+pagedown", "page_right", "Page Right", show=False),
    ]
    """Keyboard bindings for scrollable containers.

    | Key(s) | Description |
    | :- | :- |
    | up | Scroll up, if vertical scrolling is available. |
    | down | Scroll down, if vertical scrolling is available. |
    | left | Scroll left, if horizontal scrolling is available. |
    | right | Scroll right, if horizontal scrolling is available. |
    | home | Scroll to the home position, if scrolling is available. |
    | end | Scroll to the end position, if scrolling is available. |
    | pageup | Scroll up one page, if vertical scrolling is available. |
    | pagedown | Scroll down one page, if vertical scrolling is available. |
    | ctrl+pageup | Scroll left one page, if horizontal scrolling is available. |
    | ctrl+pagedown | Scroll right one page, if horizontal scrolling is available. |
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        can_focus: bool | None = None,
        can_focus_children: bool | None = None,
        can_maximize: bool | None = None,
    ) -> None:
        """
        Construct a scrollable container.

        Args:
            *children: Child widgets.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            can_focus: Can this container be focused?
            can_focus_children: Can this container's children be focused?
            can_maximized: Allow this container to maximize? `None` to use default logic.,
        """

        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        if can_focus is not None:
            self.can_focus = can_focus
        if can_focus_children is not None:
            self.can_focus_children = can_focus_children
        self.can_maximize = can_maximize

    @property
    def allow_maximize(self) -> bool:
        if self.can_maximize is None:
            return super().allow_maximize
        return self.can_maximize


class Vertical(Widget):
    """An expanding container with vertical layout and no scrollbars."""

    DEFAULT_CSS = """
    Vertical {
        width: 1fr;
        height: 1fr;
        layout: vertical;
        overflow: hidden hidden;
    }
    """


class VerticalGroup(Widget):
    """A non-expanding container with vertical layout and no scrollbars."""

    DEFAULT_CSS = """
    VerticalGroup {
        width: 1fr;
        height: auto;
        layout: vertical;
        overflow: hidden hidden;
    }
    """


class VerticalScroll(ScrollableContainer):
    """A container with vertical layout and an automatic scrollbar on the Y axis."""

    DEFAULT_CSS = """
    VerticalScroll {
        layout: vertical;
        overflow-x: hidden;
        overflow-y: auto;
    }
    """


class Horizontal(Widget):
    """An expanding container with horizontal layout and no scrollbars."""

    DEFAULT_CSS = """
    Horizontal {
        width: 1fr;
        height: 1fr;
        layout: horizontal;
        overflow: hidden hidden;
    }
    """


class HorizontalGroup(Widget):
    """A non-expanding container with horizontal layout and no scrollbars."""

    DEFAULT_CSS = """
    HorizontalGroup {
        width: 1fr;
        height: auto;
        layout: horizontal;
        overflow: hidden hidden;
    }
    """


class HorizontalScroll(ScrollableContainer):
    """A container with horizontal layout and an automatic scrollbar on the X axis."""

    DEFAULT_CSS = """
    HorizontalScroll {
        layout: horizontal;
        overflow-y: hidden;
        overflow-x: auto;
    }
    """


class Center(Widget):
    """A container which aligns children on the X axis."""

    DEFAULT_CSS = """
    Center {
        align-horizontal: center;
        width: 1fr;
        height: auto;
    }
    """


class Right(Widget):
    """A container which aligns children on the X axis."""

    DEFAULT_CSS = """
    Right {
        align-horizontal: right;
        width: 1fr;
        height: auto;
    }
    """


class Middle(Widget):
    """A container which aligns children on the Y axis."""

    DEFAULT_CSS = """
    Middle {
        align-vertical: middle;
        width: auto;
        height: 1fr;
    }
    """


class CenterMiddle(Widget):
    """A container which aligns its children on both axis."""

    DEFAULT_CSS = """
    CenterMiddle {
        align: center middle;
        width: 1fr;
        height: 1fr;
    }
    """


class Grid(Widget):
    """A container with grid layout."""

    DEFAULT_CSS = """
    Grid {
        width: 1fr;
        height: 1fr;
        layout: grid;
    }
    """


class ItemGrid(Widget):
    """A container with grid layout and automatic columns."""

    DEFAULT_CSS = """
    ItemGrid {
        width: 1fr;
        height: auto;
        layout: grid;
    }
    """

    stretch_height: reactive[bool] = reactive(True)
    min_column_width: reactive[int | None] = reactive(None, layout=True)
    max_column_width: reactive[int | None] = reactive(None, layout=True)
    regular: reactive[bool] = reactive(False)

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        min_column_width: int | None = None,
        max_column_width: int | None = None,
        stretch_height: bool = True,
        regular: bool = False,
    ) -> None:
        """
        Construct a ItemGrid.

        Args:
            *children: Child widgets.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            stretch_height: Expand the height of widgets to the row height.
            min_column_width: The smallest permitted column width.
            regular: All rows should have the same number of items.
        """
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.set_reactive(ItemGrid.stretch_height, stretch_height)
        self.set_reactive(ItemGrid.min_column_width, min_column_width)
        self.set_reactive(ItemGrid.max_column_width, max_column_width)
        self.set_reactive(ItemGrid.regular, regular)

    def pre_layout(self, layout: Layout) -> None:
        if isinstance(layout, GridLayout):
            layout.stretch_height = self.stretch_height
            layout.min_column_width = self.min_column_width
            layout.max_column_width = self.max_column_width
            layout.regular = self.regular
