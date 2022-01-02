from __future__ import annotations

from ..layout import Layout
from .dock import DockLayout
from .grid import GridLayout
from .vertical import VerticalLayout


class MissingLayout(Exception):
    pass


LAYOUT_MAP = {"dock": DockLayout, "grid": GridLayout, "vertical": VerticalLayout}


def get_layout(name: str) -> Layout:
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
        raise MissingLayout("no layout called {name!r}")
    return layout_class()
