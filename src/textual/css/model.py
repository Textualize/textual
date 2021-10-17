from __future__ import annotations

from rich import print

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .styles import Styles, StylesBuilder
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
class RuleSet:
    selectors: list[list[Selector]] = field(default_factory=list)
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
            self.selector_to_css(selector) for selector in self.selectors
        )
        declarations = "\n".join(f"    {line}" for line in self.styles.css_lines)
        css = f"{selectors} {{\n{declarations}\n}}"
        return css
