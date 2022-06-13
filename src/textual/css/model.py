from __future__ import annotations


import rich.repr

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, TYPE_CHECKING

from .styles import Styles
from .tokenize import Token
from .types import Specificity3

if TYPE_CHECKING:
    from ..dom import DOMNode


class SelectorType(Enum):
    UNIVERSAL = 1
    TYPE = 2
    CLASS = 3
    ID = 4


class CombinatorType(Enum):
    SAME = 1
    DESCENDENT = 2
    CHILD = 3


@dataclass
class Selector:
    """Represents a CSS selector.

    Some examples of selectors:

    *
    Header.title
    App > Content
    """

    name: str
    combinator: CombinatorType = CombinatorType.DESCENDENT
    type: SelectorType = SelectorType.TYPE
    pseudo_classes: list[str] = field(default_factory=list)
    specificity: Specificity3 = field(default_factory=lambda: (0, 0, 0))
    _name_lower: str = field(default="", repr=False)
    advance: int = 1

    @property
    def css(self) -> str:
        """Rebuilds the selector as it would appear in CSS."""
        pseudo_suffix = "".join(f":{name}" for name in self.pseudo_classes)
        if self.type == SelectorType.UNIVERSAL:
            return "*"
        elif self.type == SelectorType.TYPE:
            return f"{self.name}{pseudo_suffix}"
        elif self.type == SelectorType.CLASS:
            return f".{self.name}{pseudo_suffix}"
        else:
            return f"#{self.name}{pseudo_suffix}"

    def __post_init__(self) -> None:
        self._name_lower = self.name.lower()
        self._checks = {
            SelectorType.UNIVERSAL: self._check_universal,
            SelectorType.TYPE: self._check_type,
            SelectorType.CLASS: self._check_class,
            SelectorType.ID: self._check_id,
        }

    def _add_pseudo_class(self, pseudo_class: str) -> None:
        """Adds a pseudo class and updates specificity.

        Args:
            pseudo_class (str): Name of pseudo class.
        """
        self.pseudo_classes.append(pseudo_class)
        specificity1, specificity2, specificity3 = self.specificity
        self.specificity = (specificity1, specificity2 + 1, specificity3)

    def check(self, node: DOMNode) -> bool:
        """Check if a given node matches the selector.

        Args:
            node (DOMNode): A DOM node.

        Returns:
            bool: True if the selector matches, otherwise False.
        """
        return self._checks[self.type](node)

    def _check_universal(self, node: DOMNode) -> bool:
        return node.has_pseudo_class(*self.pseudo_classes)

    def _check_type(self, node: DOMNode) -> bool:
        if self._name_lower not in node._css_type_names:
            return False
        if self.pseudo_classes and not node.has_pseudo_class(*self.pseudo_classes):
            return False
        return True

    def _check_class(self, node: DOMNode) -> bool:
        if not node.has_class(self._name_lower):
            return False
        if self.pseudo_classes and not node.has_pseudo_class(*self.pseudo_classes):
            return False
        return True

    def _check_id(self, node: DOMNode) -> bool:
        if not node.id == self._name_lower:
            return False
        if self.pseudo_classes and not node.has_pseudo_class(*self.pseudo_classes):
            return False
        return True


@dataclass
class Declaration:
    token: Token
    name: str
    tokens: list[Token] = field(default_factory=list)


@rich.repr.auto(angular=True)
@dataclass
class SelectorSet:
    selectors: list[Selector] = field(default_factory=list)
    specificity: Specificity3 = (0, 0, 0)

    def __post_init__(self) -> None:
        SAME = CombinatorType.SAME
        for selector, next_selector in zip(self.selectors, self.selectors[1:]):
            selector.advance = int(next_selector.combinator != SAME)

    def __rich_repr__(self) -> rich.repr.Result:
        selectors = RuleSet._selector_to_css(self.selectors)
        yield selectors
        yield None, self.specificity

    @classmethod
    def from_selectors(cls, selectors: list[list[Selector]]) -> Iterable[SelectorSet]:
        for selector_list in selectors:
            id_total = class_total = type_total = 0
            for selector in selector_list:
                _id, _class, _type = selector.specificity
                id_total += _id
                class_total += _class
                type_total += _type
            yield SelectorSet(selector_list, (id_total, class_total, type_total))


@dataclass
class RuleSet:
    selector_set: list[SelectorSet] = field(default_factory=list)
    styles: Styles = field(default_factory=Styles)
    errors: list[tuple[Token, str]] = field(default_factory=list)
    classes: set[str] = field(default_factory=set)

    @classmethod
    def _selector_to_css(cls, selectors: list[Selector]) -> str:
        tokens: list[str] = []
        for selector in selectors:
            if selector.combinator == CombinatorType.DESCENDENT:
                tokens.append(" ")
            elif selector.combinator == CombinatorType.CHILD:
                tokens.append(" > ")
            tokens.append(selector.css)
        return "".join(tokens).strip()

    @property
    def selectors(self):
        return ", ".join(
            self._selector_to_css(selector_set.selectors)
            for selector_set in self.selector_set
        )

    @property
    def css(self) -> str:
        """Generate the CSS this RuleSet

        Returns:
            str: A string containing CSS code.
        """
        declarations = "\n".join(f"    {line}" for line in self.styles.css_lines)
        css = f"{self.selectors} {{\n{declarations}\n}}"
        return css

    def _post_parse(self) -> None:
        """Called after the RuleSet is parsed."""
        # Build a set of the class names that have been updated
        update = self.classes.update
        class_type = SelectorType.CLASS
        for selector_set in self.selector_set:
            update(
                selector.name
                for selector in selector_set.selectors
                if selector.type == class_type
            )
