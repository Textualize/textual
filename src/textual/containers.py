"""
Container widgets for quick styling.
"""

from __future__ import annotations

from typing import ClassVar

from .binding import Binding, BindingType
from .widget import Widget


class Container(Widget):
    """Simple container widget, with vertical layout."""

    DEFAULT_CSS = """
    Container {
        height: 1fr;
        layout: vertical;
        overflow: auto;
    }
    """


class ScrollableContainer(Widget, inherit_bindings=False):
    """Base container widget that binds navigation keys for scrolling."""

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
    """A container which arranges children vertically."""

    DEFAULT_CSS = """
    Vertical {
        width: 1fr;
        layout: vertical;
        overflow: hidden hidden;
    }
    """


class VerticalScroll(ScrollableContainer, can_focus=True):
    """A container which arranges children vertically, with an automatic vertical scrollbar."""

    DEFAULT_CSS = """
    VerticalScroll {
        width: 1fr;
        layout: vertical;
        overflow-y: auto;
    }
    """


class Horizontal(Widget, inherit_bindings=False):
    """A container which arranges children horizontally."""

    DEFAULT_CSS = """
    Horizontal {
        height: 1fr;
        layout: horizontal;
        overflow: hidden hidden;
    }
    """


class HorizontalScroll(ScrollableContainer, can_focus=True):
    """A container which arranges children horizontally, with an automatic horizontal scrollbar."""

    DEFAULT_CSS = """
    HorizontalScroll {
        height: 1fr;
        layout: horizontal;
        overflow-x: auto;
    }
    """


class Center(Widget, inherit_bindings=False):
    """A container which centers children horizontally."""

    DEFAULT_CSS = """
    Center {
        align-horizontal: center;
        height: auto;
        width: 1fr;
    }
    """


class Middle(Widget, inherit_bindings=False):
    """A container which aligns children vertically in the middle."""

    DEFAULT_CSS = """
    Middle {
        align-vertical: middle;
        width: auto;
        height: 1fr;
    }
    """


class Grid(Widget, inherit_bindings=False):
    """A container with grid alignment."""

    DEFAULT_CSS = """
    Grid {
        height: 1fr;
        layout: grid;
    }
    """


class Content(Widget, can_focus=True, can_focus_children=False, inherit_bindings=False):
    """A container for content such as text."""

    DEFAULT_CSS = """
    VerticalScroll {
        height: 1fr;
        layout: vertical;
        overflow-y: auto;
    }
    """
