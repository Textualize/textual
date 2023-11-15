from __future__ import annotations

from array import array
from dataclasses import dataclass
from typing import NamedTuple, Sequence

from typing_extensions import Literal, Self, TypeAlias

from ._box_drawing import BOX_CHARACTERS, Quad, box_combine_quads
from .color import Color
from .geometry import Offset

LineType: TypeAlias = Literal["thin", "heavy", "double"]
OffsetPair: TypeAlias = tuple[int, int]


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
    def render(self, canvas: Canvas) -> None:
        raise NotImplementedError()


@dataclass
class HorizontalLine(Primitive):
    origin: Offset
    length: int
    style: CanvasStyle | None = None
    line_type: LineType = "thin"

    def render(self, canvas: Canvas) -> None:
        x, y = self.origin
        box = canvas.box
        box_line = box[y]
        line_type_index = _LINE_TYPE_INDEX[self.line_type]
        combine_quads = box_combine_quads

        right = x + self.length - 1

        box_line[x] = combine_quads(box_line[x], (0, line_type_index, 0, 0))
        box_line[right] = combine_quads(box_line[right], (0, 0, 0, line_type_index))

        line_quad = (0, line_type_index, 0, line_type_index)
        for x in range(x + 1, x + self.length - 1):
            box_line[x] = combine_quads(box_line[x], line_quad)

        if self.style is not None:
            canvas.spans[y].append(_Span(x, x + self.length, self.style))


@dataclass
class VerticalLine(Primitive):
    origin: Offset
    length: int
    style: CanvasStyle | None = None
    line_type: LineType = "thin"

    def render(self, canvas: Canvas) -> None:
        x, y = self.origin
        line_type_index = _LINE_TYPE_INDEX[self.line_type]
        box = canvas.box
        combine_quads = box_combine_quads
        box[y][x] = combine_quads(box[y][x], (0, 0, line_type_index, 0))
        bottom = y + self.length - 1
        box[bottom][x] = combine_quads(box[bottom][x], (line_type_index, 0, 0, 0))
        line_quad = (line_type_index, 0, line_type_index, 0)

        for y in range(y + 1, y + self.length - 1):
            box[y][x] = combine_quads(box[y][x], line_quad)

        spans = canvas.spans
        if self.style is not None:
            span = _Span(x, x + 1, self.style)
            for y in range(y, y + self.length):
                spans[y][x] = span


@dataclass
class Rectangle(Primitive):
    origin: Offset
    width: int
    height: int
    style: CanvasStyle | None = None
    line_type: LineType = "thin"

    def render(self, canvas: Canvas) -> None:
        origin = self.origin
        width = self.width
        height = self.height
        style = self.style
        line_type = self.line_type
        HorizontalLine(origin, width, style, line_type).render(canvas)
        HorizontalLine(origin + (0, height - 1), width, style, line_type).render(canvas)
        VerticalLine(origin, height, style, line_type).render(canvas)
        VerticalLine(origin + (width - 1, 0), height, style, line_type).render(canvas)


class Canvas:
    """A character canvas."""

    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self.box: list[list[Quad]] = [[(0, 0, 0, 0)] * width for _ in range(height)]
        self.spans = [[] for _ in range(height)]

    def render(self, primitives: Sequence[Primitive]):
        for primitive in primitives:
            primitive.render(self)

        get_box = BOX_CHARACTERS.__getitem__
        for box_line in self.box:
            text = "".join([get_box(quad) for quad in box_line])
            print(text)


if __name__ == "__main__":
    canvas = Canvas(20, 20)
    primitives = [
        Rectangle(Offset(5, 5), 6, 4),
        Rectangle(Offset(6, 6), 8, 5, line_type="heavy"),
        Rectangle(Offset(8, 4), 10, 10, line_type="thin"),
        Rectangle(Offset(10, 11), 7, 4, line_type="double"),
    ]
    canvas.render(primitives)
