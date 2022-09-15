from .widget import Widget


class Container(Widget):
    """Simple container widget, with vertical layout."""

    DEFAULT_CSS = """
    Container {
        layout: vertical;
        overflow: auto;
    }
    """


class Vertical(Widget):
    """A container widget to align children vertically."""

    DEFAULT_CSS = """
    Vertical {
        layout: vertical;
        overflow-y: auto;
    }
    """


class Horizontal(Widget):
    """A container widget to align children horizontally."""

    DEFAULT_CSS = """
    Horizontal {
        layout: horizontal;
        overflow-x: hidden;
    }
    """


class Center(Widget):
    """A container widget to align children in the center."""

    DEFAULT_CSS = """
    Center {
        layout: center;
    }
    """
