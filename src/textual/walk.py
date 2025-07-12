"""
Functions for *walking* the DOM.

!!! note

    For most purposes you would be better off using [query][textual.dom.DOMNode.query], which uses these functions internally.
"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Iterable, Iterator, TypeVar, overload

if TYPE_CHECKING:
    from textual.dom import DOMNode

    WalkType = TypeVar("WalkType", bound=DOMNode)


if TYPE_CHECKING:

    @overload
    def walk_depth_first(
        root: DOMNode,
        *,
        with_root: bool = True,
    ) -> Iterable[DOMNode]: ...

    @overload
    def walk_depth_first(
        root: WalkType,
        filter_type: type[WalkType],
        *,
        with_root: bool = True,
    ) -> Iterable[WalkType]: ...


def walk_depth_first(
    root: DOMNode,
    filter_type: type[WalkType] | None = None,
    *,
    with_root: bool = True,
) -> Iterable[DOMNode] | Iterable[WalkType]:
    """Walk the tree depth first (parents first).

    !!! note

        Avoid changing the DOM (mounting, removing etc.) while iterating with this function.
        Consider [walk_children][textual.dom.DOMNode.walk_children] which doesn't have this limitation.

    Args:
        root: The root note (starting point).
        filter_type: Optional DOMNode subclass to filter by, or `None` for no filter.
        with_root: Include the root in the walk.

    Returns:
        An iterable of DOMNodes, or the type specified in `filter_type`.
    """
    stack: list[Iterator[DOMNode]] = [iter(root.children)]
    pop = stack.pop
    push = stack.append

    if filter_type is None:
        if with_root:
            yield root
        while stack:
            if (node := next(stack[-1], None)) is None:
                pop()
            else:
                yield node
                if children := node._nodes:
                    push(iter(children))
    else:
        if with_root and isinstance(root, filter_type):
            yield root
        while stack:
            if (node := next(stack[-1], None)) is None:
                pop()
            else:
                if isinstance(node, filter_type):
                    yield node
                if children := node._nodes:
                    push(iter(children))


if TYPE_CHECKING:

    @overload
    def walk_breadth_first(
        root: DOMNode,
        *,
        with_root: bool = True,
    ) -> Iterable[DOMNode]: ...

    @overload
    def walk_breadth_first(
        root: WalkType,
        filter_type: type[WalkType],
        *,
        with_root: bool = True,
    ) -> Iterable[WalkType]: ...


def walk_breadth_first(
    root: DOMNode,
    filter_type: type[WalkType] | None = None,
    *,
    with_root: bool = True,
) -> Iterable[DOMNode] | Iterable[WalkType]:
    """Walk the tree breadth first (children first).

    !!! note

        Avoid changing the DOM (mounting, removing etc.) while iterating with this function.
        Consider [walk_children][textual.dom.DOMNode.walk_children] which doesn't have this limitation.

    Args:
        root: The root note (starting point).
        filter_type: Optional DOMNode subclass to filter by, or `None` for no filter.
        with_root: Include the root in the walk.

    Returns:
        An iterable of DOMNodes, or the type specified in `filter_type`.
    """
    from textual.dom import DOMNode

    queue: deque[DOMNode] = deque()
    popleft = queue.popleft
    extend = queue.extend
    check_type = filter_type or DOMNode

    if with_root and isinstance(root, check_type):
        yield root
    extend(root.children)
    while queue:
        node = popleft()
        if isinstance(node, check_type):
            yield node
        extend(node._nodes)


def walk_breadth_search_id(
    root: DOMNode, node_id: str, *, with_root: bool = True
) -> DOMNode | None:
    """Special case to walk breadth first searching for a node with a given id.

    This is more efficient than [walk_breadth_first][textual.walk.walk_breadth_first] for this special case, as it can use an index.

    Args:
        root: The root node (starting point).
        node_id: Node id to search for.
        with_root: Consider the root node? If the root has the node id, then return it.

    Returns:
        A DOMNode if a node was found, otherwise `None`.
    """

    if with_root and root.id == node_id:
        return root

    queue: deque[DOMNode] = deque()
    queue.append(root)

    while queue:
        node = queue.popleft()
        if (found_node := node._nodes._get_by_id(node_id)) is not None:
            return found_node
        queue.extend(node._nodes)
    return None
