from __future__ import annotations

from typing import Iterable, TYPE_CHECKING
from .model import CombinatorType, Selector, SelectorSet


if TYPE_CHECKING:
    from ..dom import DOMNode


def match(selector_sets: Iterable[SelectorSet], node: DOMNode) -> bool:
    """Check if a given selector matches any of the given selector sets.

    Args:
        selector_sets (Iterable[SelectorSet]): Iterable of selector sets.
        node (DOMNode): DOM node.

    Returns:
        bool: True if the node matches the selector, otherwise False.
    """
    return any(
        _check_selectors(selector_set.selectors, node.css_path_nodes)
        for selector_set in selector_sets
    )


def _check_selectors(selectors: list[Selector], css_path_nodes: list[DOMNode]) -> bool:
    """Match a list of selectors against DOM nodes.

    Args:
        selectors (list[Selector]): A list of selectors.
        css_path_nodes (list[DOMNode]): The DOM nodes to check the selectors against.

    Returns:
        bool: True if any node in css_path_nodes matches a selector.
    """

    DESCENDENT = CombinatorType.DESCENDENT

    node = css_path_nodes[-1]
    path_count = len(css_path_nodes)
    selector_count = len(selectors)

    stack: list[tuple[int, int]] = [(0, 0)]

    push = stack.append
    pop = stack.pop
    selector_index = 0

    while stack:
        selector_index, node_index = stack[-1]
        if selector_index == selector_count or node_index == path_count:
            pop()
        else:
            path_node = css_path_nodes[node_index]
            selector = selectors[selector_index]
            if selector.combinator == DESCENDENT:
                # Find a matching descendent
                if selector.check(path_node):
                    if path_node is node and selector_index == selector_count - 1:
                        return True
                    stack[-1] = (selector_index + 1, node_index + selector.advance)
                    push((selector_index, node_index + 1))
                else:
                    stack[-1] = (selector_index, node_index + 1)
            else:
                # Match the next node
                if selector.check(path_node):
                    if path_node is node and selector_index == selector_count - 1:
                        return True
                    stack[-1] = (selector_index + 1, node_index + selector.advance)
                else:
                    pop()
    return False
