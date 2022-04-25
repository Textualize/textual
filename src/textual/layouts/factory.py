from .horizontal import HorizontalLayout
from ..layout import Layout
from ..layouts.dock import DockLayout
from ..layouts.vertical import VerticalLayout


LAYOUT_MAP = {
    "dock": DockLayout,
    "vertical": VerticalLayout,
    "horizontal": HorizontalLayout,
}


class MissingLayout(Exception):
    pass


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
        raise MissingLayout(f"no layout called {name!r}, valid layouts")
    return layout_class()
