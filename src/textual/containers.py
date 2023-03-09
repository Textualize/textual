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


class VerticalScroll(Widget):
    """A container widget which aligns children vertically and overflows if needed."""

    DEFAULT_CSS = """
    VerticalScroll {
        height: 1fr;
        layout: vertical;
        overflow-y: auto;
    }
    """


class Horizontal(Widget):
    """A container widget which aligns children horizontally."""

    DEFAULT_CSS = """
    Horizontal {
        height: 1fr;
        layout: horizontal;
        overflow-x: hidden;
    }
    """


class HorizontalScroll(Widget):
    """A container widget which aligns children horizontally and overflows if needed."""

    DEFAULT_CSS = """
    HorizontalScroll {
        height: 1fr;
        layout: horizontal;
        overflow-x: auto;
    }
    """


class Center(Widget):
    """A container widget which centers children horizontally."""

    DEFAULT_CSS = """
    Center {
        align-horizontal: center;
        width: 100%;
        height: auto;
    }
    """


class Middle(Widget):
    """A container widget which aligns children vertically in the middle."""

    DEFAULT_CSS = """
    Middle {
        align-vertical: middle;
        height: 100%;
        width: auto;
    }
    """


class Grid(Widget):
    """A container widget with grid alignment."""

    DEFAULT_CSS = """
    Grid {
        height: 1fr;
        layout: grid;
    }
    """


class Content(Widget, can_focus=True, can_focus_children=False):
    """A container for content such as text."""

    DEFAULT_CSS = """
    VerticalScroll {
        height: 1fr;
        layout: vertical;
        overflow-y: auto;
    }
    """
