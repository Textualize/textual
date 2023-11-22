"""
Container widgets for quick styling.

With the exception of `Center` and `Middle` containers will fill all of the space in the parent widget.

"""

from __future__ import annotations

from typing import ClassVar

from .binding import Binding, BindingType
from .widget import Widget


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


class ScrollableContainer(Widget, can_focus=True, inherit_bindings=False):
    """A scrollable container with vertical layout, and auto scrollbars on both axis."""

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
        Binding("left", "scroll_left", "Scroll Up", show=False),
        Binding("right", "scroll_right", "Scroll Right", show=False),
        Binding("home", "scroll_home", "Scroll Home", show=False),
        Binding("end", "scroll_end", "Scroll End", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
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
    """


class Vertical(Widget, inherit_bindings=False):
    """A container with vertical layout and no scrollbars."""

    DEFAULT_CSS = """
    Vertical {
        width: 1fr;
        height: 1fr;
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


class Horizontal(Widget, inherit_bindings=False):
    """A container with horizontal layout and no scrollbars."""

    DEFAULT_CSS = """
    Horizontal {
        width: 1fr;
        height: 1fr;
        layout: horizontal;
        overflow: hidden hidden;
    }
    """


class HorizontalScroll(ScrollableContainer):
    """A container with horizontal layout and an automatic scrollbar on the Y axis."""

    DEFAULT_CSS = """
    HorizontalScroll {
        layout: horizontal;
        overflow-y: hidden;
        overflow-x: auto;
    }
    """


class Center(Widget, inherit_bindings=False):
    """A container which aligns children on the X axis."""

    DEFAULT_CSS = """
    Center {
        align-horizontal: center;
        width: 1fr;
        height: auto;
    }
    """


class Middle(Widget, inherit_bindings=False):
    """A container which aligns children on the Y axis."""

    DEFAULT_CSS = """
    Middle {
        align-vertical: middle;
        width: auto;
        height: 1fr;
    }
    """


class Grid(Widget, inherit_bindings=False):
    """A container with grid layout."""

    DEFAULT_CSS = """
    Grid {
        width: 1fr;
        height: 1fr;
        layout: grid;
    }
    """
