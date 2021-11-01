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

    SAME = CombinatorType.SAME
    DESCENDENT = CombinatorType.DESCENDENT
    CHILD = CombinatorType.CHILD

    css_path = node.css_path
    path_count = len(css_path)
    selector_count = len(selectors)

    stack: list[tuple[int, int]] = [(0, 0)]

    push = stack.append
    pop = stack.pop
    selector_index = 0

    while stack:
        selector_index, node_index = stack[-1]
        if selector_index == selector_count:
            return node_index + 1 == path_count
        if node_index >= path_count:
            pop()
            continue
        selector = selectors[selector_index]
        path_node = css_path[node_index]
        combinator = selector.combinator
        stack[-1] = (selector_index, node_index)

        if combinator == SAME:
            # Check current node again
            if selector.check(path_node):
                stack[-1] = (selector_index + 1, node_index + selector.advance)
            else:
                pop()
        elif combinator == DESCENDENT:
            # Find a matching descendent
            if selector.check(path_node):
                pop()
                push((selector_index + 1, node_index + selector.advance + 1))
                push((selector_index + 1, node_index + selector.advance))
            else:
                stack[-1] = (selector_index, node_index + selector.advance + 1)
        elif combinator == CHILD:
            # Match the next node
            if selector.check(path_node):
                stack[-1] = (selector_index + 1, node_index + selector.advance)
            else:
                pop()
    return False
