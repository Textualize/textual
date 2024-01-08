from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, Iterable

import rich.repr

from ._help_renderables import HelpText
from .styles import Styles
from .tokenize import Token
from .types import Specificity3

if TYPE_CHECKING:
    from typing import Callable

    from typing_extensions import Self

    from ..dom import DOMNode


class SelectorType(Enum):
    """Type of selector."""

    UNIVERSAL = 1
    """i.e. * operator"""
    TYPE = 2
    """A CSS type, e.g  Label"""
    CLASS = 3
    """CSS class, e.g. .loaded"""
    ID = 4
    """CSS ID, e.g. #main"""
    NESTED = 5
    """Placeholder for nesting operator, i.e &"""


class CombinatorType(Enum):
    """Type of combinator."""

    SAME = 1
    """Selector is combined with previous selector"""
    DESCENDENT = 2
    """Selector is a descendant of the previous selector"""
    CHILD = 3
    """Selector is an immediate child of the previous selector"""


def _check_universal(name: str, node: DOMNode) -> bool:
    """Check node matches universal selector.

    Args:
        name: Selector name.
        node: A DOM node.

    Returns:
        `True` if the selector matches.
    """
    return True


def _check_type(name: str, node: DOMNode) -> bool:
    """Check node matches a type selector.

    Args:
        name: Selector name.
        node: A DOM node.

    Returns:
        `True` if the selector matches.
    """
    return name in node._css_type_names


def _check_class(name: str, node: DOMNode) -> bool:
    """Check node matches a class selector.

    Args:
        name: Selector name.
        node: A DOM node.

    Returns:
        `True` if the selector matches.
    """
    return name in node._classes


def _check_id(name: str, node: DOMNode) -> bool:
    """Check node matches an ID selector.

    Args:
        name: Selector name.
        node: A DOM node.

    Returns:
        `True` if the selector matches.
    """
    return node.id == name


_CHECKS = {
    SelectorType.UNIVERSAL: _check_universal,
    SelectorType.TYPE: _check_type,
    SelectorType.CLASS: _check_class,
    SelectorType.ID: _check_id,
    SelectorType.NESTED: _check_universal,
}


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
    pseudo_classes: set[str] = field(default_factory=set)
    specificity: Specificity3 = field(default_factory=lambda: (0, 0, 0))
    advance: int = 1

    def __post_init__(self) -> None:
        self._check: Callable[[DOMNode], bool] = partial(_CHECKS[self.type], self.name)

    @property
    def css(self) -> str:
        """Rebuilds the selector as it would appear in CSS."""
        pseudo_suffix = "".join(f":{name}" for name in sorted(self.pseudo_classes))
        if self.type == SelectorType.UNIVERSAL:
            return "*"
        elif self.type == SelectorType.TYPE:
            return f"{self.name}{pseudo_suffix}"
        elif self.type == SelectorType.CLASS:
            return f".{self.name}{pseudo_suffix}"
        else:
            return f"#{self.name}{pseudo_suffix}"

    def _add_pseudo_class(self, pseudo_class: str) -> None:
        """Adds a pseudo class and updates specificity.

        Args:
            pseudo_class: Name of pseudo class.
        """
        self.pseudo_classes.add(pseudo_class)
        specificity1, specificity2, specificity3 = self.specificity
        self.specificity = (specificity1, specificity2 + 1, specificity3)

    def check(self, node: DOMNode) -> bool:
        """Check if a given node matches the selector.

        Args:
            node: A DOM node.

        Returns:
            True if the selector matches, otherwise False.
        """
        return self._check(node) and (
            node.has_pseudo_classes(self.pseudo_classes)
            if self.pseudo_classes
            else True
        )


@dataclass
class Declaration:
    """A single CSS declaration (not yet processed)."""

    token: Token
    name: str
    tokens: list[Token] = field(default_factory=list)


@rich.repr.auto(angular=True)
@dataclass
class SelectorSet:
    """A set of selectors associated with a rule set."""

    selectors: list[Selector] = field(default_factory=list)
    specificity: Specificity3 = (0, 0, 0)

    def __post_init__(self) -> None:
        SAME = CombinatorType.SAME
        for selector, next_selector in zip(self.selectors, self.selectors[1:]):
            selector.advance = int(next_selector.combinator != SAME)

    @property
    def css(self) -> str:
        return RuleSet._selector_to_css(self.selectors)

    def __rich_repr__(self) -> rich.repr.Result:
        selectors = RuleSet._selector_to_css(self.selectors)
        yield selectors
        yield None, self.specificity

    def _total_specificity(self) -> Self:
        """Calculate total specificity of selectors.

        Returns:
            Self.
        """
        id_total = class_total = type_total = 0
        for selector in self.selectors:
            _id, _class, _type = selector.specificity
            id_total += _id
            class_total += _class
            type_total += _type
        self.specificity = (id_total, class_total, type_total)
        return self

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
    errors: list[tuple[Token, str | HelpText]] = field(default_factory=list)

    is_default_rules: bool = False
    tie_breaker: int = 0
    selector_names: set[str] = field(default_factory=set)
    pseudo_classes: set[str] = field(default_factory=set)

    def __hash__(self):
        return id(self)

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
            A string containing CSS code.
        """
        declarations = "\n".join(f"    {line}" for line in self.styles.css_lines)
        css = f"{self.selectors} {{\n{declarations}\n}}"
        return css

    def _post_parse(self) -> None:
        """Called after the RuleSet is parsed."""
        # Build a set of the class names that have been updated

        class_type = SelectorType.CLASS
        id_type = SelectorType.ID
        type_type = SelectorType.TYPE
        universal_type = SelectorType.UNIVERSAL

        add_selector = self.selector_names.add
        add_pseudo_classes = self.pseudo_classes.update

        for selector_set in self.selector_set:
            for selector in selector_set.selectors:
                add_pseudo_classes(selector.pseudo_classes)

            selector = selector_set.selectors[-1]
            selector_type = selector.type
            if selector_type == universal_type:
                add_selector("*")
            elif selector_type == type_type:
                add_selector(selector.name)
            elif selector_type == class_type:
                add_selector(f".{selector.name}")
            elif selector_type == id_type:
                add_selector(f"#{selector.name}")
