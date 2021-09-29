from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


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
class RuleSet:
    selectors: list[list[Selector]] = field(default_factory=list)
    declarations: list[Declaration] = field(default_factory=list)


@dataclass
class Selector:
    name: str
    combinator: CombinatorType = CombinatorType.SAME
    selector: SelectorType = SelectorType.TYPE
    pseudo_classes: list[str] = field(default_factory=list)


@dataclass
class Declaration:
    name: str
    tokens: list[tuple[str, str]] = field(default_factory=list)
