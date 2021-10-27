from __future__ import annotations

from rich import print

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .styles import Styles
from .tokenize import Token


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


@dataclass
class Selector:
    name: str
    combinator: CombinatorType = CombinatorType.SAME
    selector: SelectorType = SelectorType.TYPE
    pseudo_classes: list[str] = field(default_factory=list)
    specificity: tuple[int, int, int] = field(default_factory=lambda: (0, 0, 0))

    @property
    def css(self) -> str:
        psuedo_suffix = "".join(f":{name}" for name in self.pseudo_classes)
        if self.selector == SelectorType.UNIVERSAL:
            return "*"
        elif self.selector == SelectorType.TYPE:
            return f"{self.name}{psuedo_suffix}"
        elif self.selector == SelectorType.CLASS:
            return f".{self.name}{psuedo_suffix}"
        else:
            return f"#{self.name}{psuedo_suffix}"


@dataclass
class Declaration:
    name: str
    tokens: list[Token] = field(default_factory=list)

    def process(self):
        raise NotImplementedError


@dataclass
class SelectorSet:
    selectors: list[Selector] = field(default_factory=list)
    specificity: tuple[int, int, int] = (0, 0, 0)

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
