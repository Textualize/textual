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


class Vertical(Widget):
    """A container widget which aligns children vertically."""

    DEFAULT_CSS = """
    Vertical {
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
    Vertical {
        height: 1fr;
        layout: vertical;
        overflow-y: auto;
    }
    """
