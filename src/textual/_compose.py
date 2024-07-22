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
    from .widget import MountError, Widget

    app = node.app
    nodes: list[Widget] = []
    compose_stack: list[Widget] = []
    composed: list[Widget] = []
    app._compose_stacks.append(compose_stack)
    app._composed.append(composed)
    iter_compose = iter(node.compose())
    is_generator = hasattr(iter_compose, "throw")
    try:
        while True:
            try:
                child = next(iter_compose)
            except StopIteration:
                break

            if not isinstance(child, Widget):
                mount_error = MountError(
                    f"Can't mount {type(child)}; expected a Widget instance."
                )
                if is_generator:
                    iter_compose.throw(mount_error)  # type: ignore
                else:
                    raise mount_error from None

            try:
                child.id
            except AttributeError:
                mount_error = MountError(
                    "Widget is missing an 'id' attribute; did you forget to call super().__init__()?"
                )
                if is_generator:
                    iter_compose.throw(mount_error)  # type: ignore
                else:
                    raise mount_error from None

            if composed:
                nodes.extend(composed)
                composed.clear()
            if compose_stack:
                try:
                    compose_stack[-1].compose_add_child(child)
                except Exception as error:
                    if is_generator:
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


def _pending_children(
    node: Widget, children_by_id: dict[str, Widget]
) -> dict[str, Widget]:
    def recurse_children(widget: Widget):
        children: list[Widget] = list(
            child
            for child in widget._pending_children
            if not child.has_class("-textual-system")
        )

        if widget.id is not None and widget.id not in children_by_id:
            children_by_id[widget.id] = widget
        for child in children:
            recurse_children(child)

    recurse_children(node)

    return children_by_id


def recompose(
    node: App | Widget, compose_node: App | Widget | None = None
) -> tuple[list[Widget], set[Widget]]:
    """Recompose a node (nodes with a matching nodes will have their state copied).

    Args:
        node: Node to be recomposed.
        compose_node: Node where new nodes are composed, or `None` for the same node.

    Returns:
        A list of new nodes, and a list of nodes to be removed.
    """
    children: list[Widget] = list(
        child for child in node._nodes if not child.has_class("-textual-system")
    )
    children_by_id = {child.id: child for child in children if child.id is not None}
    new_children: list[Widget] = []
    remove_children: set[Widget] = set(children)

    composed = compose(node if compose_node is None else compose_node)

    for compose_node in compose(node if compose_node is None else compose_node):
        _pending_children(compose_node, children_by_id)

    def recurse_pending(node: Widget) -> None:
        print("recurse", node, children_by_id)
        for child in list(node._nodes):
            if child.id is not None and child.id in children_by_id:
                print(1)
                existing_child = children_by_id.pop(child.id)
                if node._nodes._replace(child, existing_child):
                    remove_children.add(child)
            else:
                print(2)
                recurse_pending(child)

    for compose_node in composed:
        if (
            compose_node.id is not None
            and (existing_child := children_by_id.pop(compose_node.id, None))
            is not None
        ):
            new_children.append(existing_child)
            remove_children.discard(existing_child)
            existing_child.copy_state(compose_node)
        else:
            new_children.append(compose_node)
            recurse_pending(node)

    node.log(children_by_id)
    print(new_children, remove_children)

    return (new_children, remove_children)
