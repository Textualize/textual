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
    _rich_traceback_omit = True
    app = node.app
    nodes: list[Widget] = []
    compose_stack: list[Widget] = []
    composed: list[Widget] = []
    app._compose_stacks.append(compose_stack)
    app._composed.append(composed)
    iter_compose = iter(node.compose())
    try:
        while True:
            try:
                child = next(iter_compose)
            except StopIteration:
                break
            if composed:
                nodes.extend(composed)
                composed.clear()
            if compose_stack:
                try:
                    compose_stack[-1].compose_add_child(child)
                except Exception as error:
                    if hasattr(iter_compose, "throw"):
                        # So the error is raised inside the generator
                        # This will generate a more sensible traceback for the dev
                        iter_compose.throw(error)  # type: ignore
                    else:
                        raise
            else:
                nodes.append(child)
        if composed:
            nodes.extend(composed)
            composed.clear()
    finally:
        app._compose_stacks.pop()
        app._composed.pop()
    return nodes
