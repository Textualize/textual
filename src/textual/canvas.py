from array import array
from dataclasses import dataclass
from typing import NamedTuple

from typing_extensions import Literal, Self, TypeAlias

from ._box_drawing import box_combine_quad
from ._loop import loop_first_last
from .color import Color
from .geometry import Offset

LineType: TypeAlias = Literal["thin", "heavy", "double"]
OffsetPair: TypeAlias = tuple[int, int]

_HORIZONTAL = {
    "thin": "╶─╴",
    "heavy": "╺━╸",
    "double": "╺═╸",
}
_VERTICAL = {
    "thin": "╷│╵",
    "heavy": "╻┃╹",
    "double": "╻║╹",
}

_LINE_TYPE_INDEX = {"thin": 1, "heavy": 2, "double": 3}


class CanvasStyle(NamedTuple):
    foreground: Color = Color(255, 255, 255)
    background: Color = Color(0, 0, 0, 0)
    bold: bool = False
    italic: bool = False
    underline: bool = False

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


Lines: TypeAlias = list["array[str]"]
Spans: TypeAlias = list[list[_Span]]


class Primitive:
    def render(self, lines: Lines, spans: Spans) -> None:
        raise NotImplementedError()


@dataclass
class HorizontalLine(Primitive):
    origin: Offset
    length: int
    style: CanvasStyle | None = None
    line_type: LineType = "thin"
    start: bool = True
    end: bool = True

    def render(self, lines: Lines, spans: Spans) -> None:
        x, y = self.origin
        line = lines[y]
        line_type_index = _LINE_TYPE_INDEX[self.line_type]
        for start, end, x in loop_first_last(range(x, x + self.length)):
            line[x] = box_combine_quad(
                line[x],
                (0, 0 if end else line_type_index, 0, 0 if start else line_type_index),
            )
        if self.style is not None:
            spans[y].append(_Span(x, x + self.length, self.style))


@dataclass
class VerticalLine(Primitive):
    origin: Offset
    length: int
    style: CanvasStyle | None = None
    line_type: LineType = "thin"

    def render(self, lines: Lines, spans: Spans) -> None:
        x, y = self.origin
        line_type_index = _LINE_TYPE_INDEX[self.line_type]
        for start, end, y in loop_first_last(range(y, y + self.length)):
            lines[y][x] = box_combine_quad(
                lines[y][x],
                (0 if start else line_type_index, 0, 0 if end else line_type_index, 0),
            )

        if self.style is not None:
            span = _Span(x, x + 1, self.style)
            for start, end, y in loop_first_last(range(y, y + self.length)):
                spans[y][x] = span


@dataclass
class _Rectangle(Primitive):
    origin: Offset
    width: int
    height: int


class Canvas:
    """A character canvas."""

    def __init__(self) -> None:
        self._primitives: list[Primitive] = []

    def clear(self) -> None:
        self._primitives.clear()

    def add(self, primitive: Primitive) -> None:
        self._primitives.append(primitive)

    def render(self, width: int, height: int):
        lines = [array("u", " " * width) for _ in range(height)]
        spans: list[list[_Span]] = [[] for _ in range(height)]

        for primitive in self._primitives:
            primitive.render(lines, spans)

        for line in lines:
            print(line.tounicode())


if __name__ == "__main__":
    canvas = Canvas()
    canvas.add(HorizontalLine(Offset(2, 3), 10))
    canvas.add(VerticalLine(Offset(2, 3), 5, line_type="heavy"))
    canvas.render(20, 10)
