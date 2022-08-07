from .widget import Widget


class Vertical(Widget):
    """A container widget to align children vertically."""

    CSS = """
    Vertical {
        layout: vertical;       
        overflow: auto;
    }    
    """


class Horizontal(Widget):
    """A container widget to align children horizontally."""

    CSS = """
    Horizontal {
        layout: horizontal;
        overflow: auto;
    }    
    """


class Center(Widget):
    """A container widget to align children in the center."""

    CSS = """
    Center {
        layout: center;
        overflow: auto;
    }
    
    """
