from __future__ import annotations

from typing import Iterable, TYPE_CHECKING
from .model import CombinatorType, Selector, SelectorSet, SelectorType


if TYPE_CHECKING:
    from ..dom import DOMNode


def match(selector_sets: Iterable[SelectorSet], node: DOMNode):
    for selector_set in selector_sets:
        if _check_selectors(selector_set.selectors, node):
            return True
    return False


def _check_selectors(selectors: list[Selector], node: DOMNode) -> bool:

    DESCENDENT = CombinatorType.DESCENDENT

    css_path = node.css_path
    path_count = len(css_path)
    selector_count = len(selectors)

    stack: list[tuple[int, int]] = [(0, 0)]

    push = stack.append
    pop = stack.pop
    selector_index = 0

    while stack:
        selector_index, node_index = stack[-1]
        if selector_index == selector_count or node_index == path_count:
            pop()
            continue
        last_selector = selector_index == selector_count - 1
        path_node = css_path[node_index]
        selector = selectors[selector_index]
        advance = selector.advance
        combinator = selector.combinator

        if combinator == DESCENDENT:
            # Find a matching descendent
            if selector.check(path_node):
                if path_node is node and last_selector:
                    return True
                stack[-1] = (selector_index + 1, node_index + advance)
                push((selector_index, node_index + 1))
            else:
                stack[-1] = (selector_index, node_index + 1)
        else:
            # Match the next node
            if selector.check(path_node):
                if path_node is node and last_selector:
                    return True
                stack[-1] = (selector_index + 1, node_index + advance)
            else:
                pop()
    return False
