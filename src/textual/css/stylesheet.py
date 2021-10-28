from __future__ import annotations

import rich.repr

from ..dom import DOMNode
from .errors import StylesheetError
from .model import CombinatorType, RuleSet, Selector, SelectorType
from .parse import parse
from .styles import Styles
from .types import Specificity3


@rich.repr.auto
class Stylesheet:
    def __init__(self) -> None:
        self.rules: list[RuleSet] = []

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.rules

    @property
    def css(self) -> str:
        return "\n\n".join(rule_set.css for rule_set in self.rules)

    def read(self, filename: str) -> None:
        try:
            with open(filename, "rt") as css_file:
                css = css_file.read()
        except Exception as error:
            raise StylesheetError(f"unable to read {filename!r}; {error}") from None
        try:
            rules = list(parse(css))
        except Exception as error:
            raise StylesheetError(f"failed to parse {filename!r}; {error}") from None
        self.rules.extend(rules)

    def parse(self, css: str) -> None:
        try:
            rules = list(parse(css))
        except Exception as error:
            raise StylesheetError(f"failed to parse css; {error}") from None
        self.rules.extend(rules)

    def apply(self, node: DOMNode) -> None:
        styles: list[tuple[Specificity3, Styles]] = []

        for rule in self.rules:
            self.apply_rule(rule, node)

    def apply_rule(self, rule: RuleSet, node: DOMNode) -> None:
        for selector_set in rule.selector_set:
            self.check_selectors(selector_set.selectors, node)

    def check_selectors(self, selectors: list[Selector], node: DOMNode) -> bool:
        node_path = node.css_path
        nodes = iter(node_path)

        node_siblings = next(nodes, None)
        if node_siblings is None:
            return False
        node, siblings = node_siblings

        for selector in selectors:
            if selector.type == SelectorType.UNIVERSAL:
                continue
            elif selector.type == SelectorType.TYPE:
                while node.css_type != selector.name:
                    node_siblings = next(nodes, None)
                    if node_siblings is None:
                        return False
                    node, siblings = node_siblings
            elif selector.type == SelectorType.CLASS:
                while node.css_type != selector.name:
                    node_siblings = next(nodes, None)
                    if node_siblings is None:
                        return False
                    node, siblings = node_siblings
        return True
