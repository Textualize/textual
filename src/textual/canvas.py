from array import array
from dataclasses import dataclass
from typing import NamedTuple

from typing_extensions import Literal, Self, TypeAlias

from textual.color import Color
from textual.geometry import Offset

LineType: TypeAlias = Literal["thin", "heavy", "double"]
OffsetPair: TypeAlias = tuple[int, int]


class CanvasStyle(NamedTuple):
    foreground: Color
    background: Color = Color(0, 0, 0, 0)
    bold: bool = False
    italic: bool = False
    underline: bool = True

    def __add__(self, other: Self) -> Self:
        foreground1, background1, bold1, italic1, underline1 = self
        foreground2, background2, bold2, italic2, underline2 = other
        return CanvasStyle(
            foreground1 + foreground2,
            background1 + background2,
            bold1 or bold2,
            italic1 or italic2,
            underline1 or underline2,
        )


class _Span(NamedTuple):
    start: int
    end: int
    style: CanvasStyle


Lines: TypeAlias = list[array[str]]
Spans: TypeAlias = list[list[_Span]]


class Primitive:
    def render(self, lines: Lines, spans: Spans) -> None:
        raise NotImplementedError()


@dataclass
class _HorizontalLine(Primitive):
    start: Offset
    length: int


@dataclass
class _Rectangle(Primitive):
    origin: Offset
    width: int
    height: int


class Canvas:
    def __init__(self) -> None:
        self._primitives: list[Primitive] = []

    def clear(self) -> None:
        self._primitives.clear()

    def horizontal_line(self, origin: Offset, length: int) -> None:
        self._primitives.append(_HorizontalLine(origin, length))

    def render(self, width: int, height: int, background: Color, foreground: Color):
        lines = [array("u", " " * width) for _ in range(height)]
        spans: list[list[_Span]] = [[] for _ in range(height)]

        for primitive in self._primitives:
            primitive.render(lines, spans)
