from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App
    from .widget import Widget


def compose(node: App | Widget) -> list[Widget]:
    """Compose child widgets.

    Args:
        node: The parent node.

    Returns:
        A list of widgets.
    """
    app = node.app
    nodes: list[Widget] = []
    for child in node.compose():
        if app._composed:
            nodes.extend(app._composed)
            app._composed.clear()
        if app._compose_stack:
            app._compose_stack[-1]._nodes._append(child)
        else:
            nodes.append(child)
    if app._composed:
        nodes.extend(app._composed)
        app._composed.clear()
    return nodes
