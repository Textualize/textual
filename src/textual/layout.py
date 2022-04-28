from .widget import Widget


class Vertical(Widget):
    """A container widget to align children vertically."""

    CSS = """
    Vertical {
        layout: vertical;       
    }    
    """


class Horizontal(Widget):
    """A container widget to align children horizontally."""

    CSS = """
    Horizontal {
        layout: horizontal;
    }    
    """
