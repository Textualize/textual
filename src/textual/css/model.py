from __future__ import annotations

from typing import Callable

from rich import print

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from ..dom import DOMNode
from .styles import Styles
from .tokenize import Token
from .types import Specificity3


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
class Location:
    line: tuple[int, int]
    column: tuple[int, int]


def _default_check(node: DOMNode) -> bool | None:
    return True


@dataclass
class Selector:
    name: str
    combinator: CombinatorType = CombinatorType.DESCENDENT
    type: SelectorType = SelectorType.TYPE
    pseudo_classes: list[str] = field(default_factory=list)
    specificity: Specificity3 = field(default_factory=lambda: (0, 0, 0))
    _name_lower: str = ""

    @property
    def css(self) -> str:
        psuedo_suffix = "".join(f":{name}" for name in self.pseudo_classes)
        if self.type == SelectorType.UNIVERSAL:
            return "*"
        elif self.type == SelectorType.TYPE:
            return f"{self.name}{psuedo_suffix}"
        elif self.type == SelectorType.CLASS:
            return f".{self.name}{psuedo_suffix}"
        else:
            return f"#{self.name}{psuedo_suffix}"

    def __post_init__(self) -> None:
        self._name_lower = self.name.lower()
        self._checks = {
            SelectorType.UNIVERSAL: self._check_universal,
            SelectorType.TYPE: self._check_type,
            SelectorType.CLASS: self._check_class,
            SelectorType.ID: self._check_id,
        }

    def check(self, node: DOMNode) -> bool | None:
        return self._checks[self.type](node)

    def _check_universal(self, node: DOMNode) -> bool | None:
        return True

    def _check_type(self, node: DOMNode) -> bool | None:
        if node.css_type != self._name_lower:
            return False
        if self.pseudo_classes and not node.has_psuedo_class(*self.pseudo_classes):
            return False
        return True

    def _check_class(self, node: DOMNode) -> bool | None:
        if not node.has_class(self._name_lower):
            return False
        if self.pseudo_classes and not node.has_psuedo_class(*self.pseudo_classes):
            return False
        return True

    def _check_id(self, node: DOMNode) -> bool | None:
        if not node.id == self._name_lower:
            return False
        if self.pseudo_classes and not node.has_psuedo_class(*self.pseudo_classes):
            return False
        return True


@dataclass
class Declaration:
    name: str
    tokens: list[Token] = field(default_factory=list)


@dataclass
class SelectorSet:
    selectors: list[Selector] = field(default_factory=list)
    specificity: Specificity3 = (0, 0, 0)

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

    @classmethod
    def selector_to_css(cls, selectors: list[Selector]) -> str:
        tokens: list[str] = []
        for selector in selectors:
            if selector.combinator == CombinatorType.DESCENDENT:
                tokens.append(" ")
            elif selector.combinator == CombinatorType.CHILD:
                tokens.append(" > ")
            tokens.append(selector.css)
        return "".join(tokens).strip()

    @property
    def css(self) -> str:
        selectors = ", ".join(
            self.selector_to_css(selector_set.selectors)
            for selector_set in self.selector_set
        )
        declarations = "\n".join(f"    {line}" for line in self.styles.css_lines)
        css = f"{selectors} {{\n{declarations}\n}}"
        return css
