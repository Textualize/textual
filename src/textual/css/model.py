from __future__ import annotations

from rich import print

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

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
