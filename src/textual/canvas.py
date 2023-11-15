from __future__ import annotations

from array import array
from collections import defaultdict
from dataclasses import dataclass
from operator import itemgetter
from typing import NamedTuple, Sequence

from rich.segment import Segment
from rich.style import Style
from typing_extensions import Literal, TypeAlias

from ._box_drawing import BOX_CHARACTERS, Quad, box_combine_quads
from .color import Color
from .geometry import Offset
from .strip import Strip

LineType: TypeAlias = Literal["thin", "heavy", "double"]
OffsetPair: TypeAlias = tuple[int, int]


_LINE_TYPE_INDEX = {"thin": 1, "heavy": 2, "double": 3}


class _Span(NamedTuple):
    """Associates a sequence of character indices with a color."""

    start: int
    end: int  # exclusive
    color: Color


class Primitive:
    """Base class for a canvas primitive."""

    def render(self, canvas: Canvas) -> None:
        raise NotImplementedError()


@dataclass
class HorizontalLine(Primitive):
    origin: Offset
    length: int
    color: Color
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
        for box_x in range(x + 1, x + self.length - 1):
            box_line[box_x] = combine_quads(box_line[box_x], line_quad)

        canvas.spans[y].append(_Span(x, x + self.length, self.color))


@dataclass
class VerticalLine(Primitive):
    origin: Offset
    length: int
    color: Color
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

        for box_y in range(y + 1, y + self.length - 1):
            box[box_y][x] = combine_quads(box[box_y][x], line_quad)

        spans = canvas.spans
        span = _Span(x, x + 1, self.color)
        for y in range(y, y + self.length):
            spans[y].append(span)


@dataclass
class Rectangle(Primitive):
    origin: Offset
    width: int
    height: int
    color: Color
    line_type: LineType = "thin"

    def render(self, canvas: Canvas) -> None:
        origin = self.origin
        width = self.width
        height = self.height
        color = self.color
        line_type = self.line_type
        HorizontalLine(origin, width, color, line_type).render(canvas)
        HorizontalLine(origin + (0, height - 1), width, color, line_type).render(canvas)
        VerticalLine(origin, height, color, line_type).render(canvas)
        VerticalLine(origin + (width - 1, 0), height, color, line_type).render(canvas)


class Canvas:
    """A character canvas."""

    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self.lines: list[array[str]] = [array("u", " " * width) for _ in range(height)]
        self.box: list[defaultdict[int, Quad]] = [
            defaultdict(lambda: (0, 0, 0, 0)) for _ in range(height)
        ]
        self.spans: list[list[_Span]] = [[] for _ in range(height)]

    def render(self, primitives: Sequence[Primitive], base_style: Style) -> list[Strip]:
        for primitive in primitives:
            primitive.render(self)

        get_box = BOX_CHARACTERS.__getitem__
        for box, line in zip(self.box, self.lines):
            for offset, quad in box.items():
                line[offset] = get_box(quad)

        width = self._width
        span_sort_key = itemgetter(0, 1)
        strips: list[Strip] = []
        color = Color.parse("transparent")

        _Segment = Segment
        for raw_spans, line in zip(self.spans, self.lines):
            text = line.tounicode()

            if raw_spans:
                segments: list[Segment] = []

                enumerated_spans = list(enumerate(raw_spans, 1))
                style_map = {index: span.color for index, span in enumerated_spans}
                style_map[0] = color

                spans = [
                    (0, False, 0),
                    *((span.start, False, index) for index, span in enumerated_spans),
                    *((span.end, True, index) for index, span in enumerated_spans),
                    (width, True, 0),
                ]
                spans.sort(key=span_sort_key)
                stack: list[int] = []
                stack_pop = stack.remove
                stack_append = stack.append
                for (offset, leaving, style_id), (next_offset, _, _) in zip(
                    spans, spans[1:]
                ):
                    if leaving:
                        stack_pop(style_id)
                    else:
                        stack_append(style_id)
                    if next_offset > offset:
                        segment_color = color
                        for _color in sorted(stack):
                            segment_color += style_map[_color]

                        segments.append(
                            _Segment(
                                text[offset:next_offset],
                                base_style + Style(color=segment_color.rich_color),
                            )
                        )
                strips.append(Strip(segments, width))
            else:
                strips.append(Strip([_Segment(text, base_style)], width))

        return strips


if __name__ == "__main__":
    canvas = Canvas(30, 20)
    primitives = [
        Rectangle(Offset(5, 5), 6, 4, Color.parse("rgba(255, 0,0,0.5)")),
        Rectangle(Offset(6, 6), 8, 5, Color.parse("green"), line_type="heavy"),
        Rectangle(Offset(8, 4), 10, 10, Color.parse("blue"), line_type="thin"),
        Rectangle(Offset(10, 11), 7, 4, Color.parse("magenta"), line_type="double"),
    ]
    strips = canvas.render(primitives, Style.parse("white on #000000"))

    from rich.console import Console

    console = Console()

    for strip in strips:
        print(strip.render(console))
