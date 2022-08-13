from .widget import Widget


class Container(Widget):
    """Simple container widget, with vertical layout."""

    CSS = """
    Container {
        layout: vertical;       
        overflow: auto;
    }    
    """


class Vertical(Container):
    """A container widget to align children vertically."""

    # Blank CSS is important, otherwise you get a clone of Container
    CSS = ""


class Horizontal(Container):
    """A container widget to align children horizontally."""

    CSS = """
    Horizontal {
        layout: horizontal;        
    }    
    """


class Center(Container):
    """A container widget to align children in the center."""

    CSS = """
    Center {
        layout: center;        
    }
    """
