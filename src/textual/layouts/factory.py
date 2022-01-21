from typing import Literal

from ..layout import Layout
from ..layouts.dock import DockLayout
from ..layouts.grid import GridLayout
from ..layouts.vertical import VerticalLayout

LayoutName = Literal["dock", "grid", "vertical"]
LAYOUT_MAP = {"dock": DockLayout, "grid": GridLayout, "vertical": VerticalLayout}


class MissingLayout(Exception):
    pass


def get_layout(name: LayoutName) -> Layout:
    """Get a named layout object.

    Args:
        name (str): Name of the layout.

    Raises:
        MissingLayout: If the named layout doesn't exist.

    Returns:
        Layout: A layout object.
    """

    layout_class = LAYOUT_MAP.get(name)
    if layout_class is None:
        raise MissingLayout(f"no layout called {name!r}, valid layouts")
    return layout_class()
