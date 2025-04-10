"""
A Canvas class used to render keylines.

!!! note
    This API is experimental, and may change in the near future.

"""

from __future__ import annotations

import sys
from array import array
from collections import defaultdict
from dataclasses import dataclass
from operator import itemgetter
from typing import NamedTuple, Sequence

from rich.segment import Segment
from rich.style import Style
from typing_extensions import Literal, TypeAlias

from textual._box_drawing import BOX_CHARACTERS, Quad, combine_quads
from textual.color import Color
from textual.geometry import Offset, clamp
from textual.strip import Strip, StripRenderable

CanvasLineType: TypeAlias = Literal["thin", "heavy", "double"]


_LINE_TYPE_INDEX = {"thin": 1, "heavy": 2, "double": 3}


class _Span(NamedTuple):
    """Associates a sequence of character indices with a color."""

    start: int
    end: int  # exclusive
    color: Color


class Primitive:
    """Base class for a canvas primitive."""

    def render(self, canvas: Canvas) -> None:
        """Render to the canvas.

        Args:
            canvas: Canvas instance.
        """
        raise NotImplementedError()


@dataclass
class HorizontalLine(Primitive):
    """A horizontal line."""

    origin: Offset
    length: int
    color: Color
    line_type: CanvasLineType = "thin"

    def render(self, canvas: Canvas) -> None:
        x, y = self.origin
        if y < 0 or y > canvas.height - 1:
            return
        box = canvas.box
        box_line = box[y]

        line_type_index = _LINE_TYPE_INDEX[self.line_type]
        _combine_quads = combine_quads

        right = x + self.length - 1

        x_range = canvas.x_range(x, x + self.length)

        if x in x_range:
            box_line[x] = _combine_quads(box_line[x], (0, line_type_index, 0, 0))
        if right in x_range:
            box_line[right] = _combine_quads(
                box_line[right], (0, 0, 0, line_type_index)
            )

        line_quad = (0, line_type_index, 0, line_type_index)
        for box_x in canvas.x_range(x + 1, x + self.length - 1):
            box_line[box_x] = _combine_quads(box_line[box_x], line_quad)

        canvas.spans[y].append(_Span(x, x + self.length, self.color))


@dataclass
class VerticalLine(Primitive):
    """A vertical line."""

    origin: Offset
    length: int
    color: Color
    line_type: CanvasLineType = "thin"

    def render(self, canvas: Canvas) -> None:
        x, y = self.origin
        if x < 0 or x >= canvas.width:
            return
        line_type_index = _LINE_TYPE_INDEX[self.line_type]
        box = canvas.box
        _combine_quads = combine_quads

        y_range = canvas.y_range(y, y + self.length)

        if y in y_range:
            box[y][x] = _combine_quads(box[y][x], (0, 0, line_type_index, 0))
        bottom = y + self.length - 1

        if bottom in y_range:
            box[bottom][x] = _combine_quads(box[bottom][x], (line_type_index, 0, 0, 0))
        line_quad = (line_type_index, 0, line_type_index, 0)

        for box_y in canvas.y_range(y + 1, y + self.length - 1):
            box[box_y][x] = _combine_quads(box[box_y][x], line_quad)

        spans = canvas.spans
        span = _Span(x, x + 1, self.color)
        for y in y_range:
            spans[y].append(span)


@dataclass
class Rectangle(Primitive):
    """A rectangle."""

    origin: Offset
    width: int
    height: int
    color: Color
    line_type: CanvasLineType = "thin"

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
        """

        Args:
            width: Width of the canvas (in cells).
            height Height of the canvas (in cells).
        """
        self._width = width
        self._height = height
        blank_line = " " * width
        array_type_code = "w" if sys.version_info >= (3, 13) else "u"
        self.lines: list[array[str]] = [
            array(array_type_code, blank_line) for _ in range(height)
        ]
        self.box: list[defaultdict[int, Quad]] = [
            defaultdict(lambda: (0, 0, 0, 0)) for _ in range(height)
        ]
        self.spans: list[list[_Span]] = [[] for _ in range(height)]

    @property
    def width(self) -> int:
        """The canvas width."""
        return self._width

    @property
    def height(self) -> int:
        """The canvas height."""
        return self._height

    def x_range(self, start: int, end: int) -> range:
        """Range of x values, clipped to the canvas dimensions.

        Args:
            start: Start index.
            end: End index.

        Returns:
            A range object.
        """
        return range(
            clamp(start, 0, self._width),
            clamp(end, 0, self._width),
        )

    def y_range(self, start: int, end: int) -> range:
        """Range of y values, clipped to the canvas dimensions.

        Args:
            start: Start index.
            end: End index.

        Returns:
            A range object.
        """
        return range(
            clamp(start, 0, self._height),
            clamp(end, 0, self._height),
        )

    def render(
        self, primitives: Sequence[Primitive], base_style: Style
    ) -> StripRenderable:
        """Render the canvas.

        Args:
            primitives: A sequence of primitives.
            base_style: The base style of the canvas.

        Returns:
            A Rich renderable for the canvas.
        """
        for primitive in primitives:
            primitive.render(self)

        get_box = BOX_CHARACTERS.__getitem__
        for box, line in zip(self.box, self.lines):
            for offset, quad in box.items():
                line[offset] = get_box(quad)

        width = self._width
        span_sort_key = itemgetter(0, 1)
        strips: list[Strip] = []
        color = (
            Color.from_rich_color(base_style.bgcolor)
            if base_style.bgcolor
            else Color.parse("transparent")
        )
        _Segment = Segment
        for raw_spans, line in zip(self.spans, self.lines):
            text = line.tounicode()

            if raw_spans:
                segments: list[Segment] = []
                colors = [color] + [span.color for span in raw_spans]
                spans = [
                    (0, False, 0),
                    *(
                        (span.start, False, index)
                        for index, span in enumerate(raw_spans, 1)
                    ),
                    *(
                        (span.end, True, index)
                        for index, span in enumerate(raw_spans, 1)
                    ),
                    (width, True, 0),
                ]
                spans.sort(key=span_sort_key)
                color_indices: set[int] = set()
                color_remove = color_indices.discard
                color_add = color_indices.add
                for (offset, leaving, style_id), (next_offset, _, _) in zip(
                    spans, spans[1:]
                ):
                    if leaving:
                        color_remove(style_id)
                    else:
                        color_add(style_id)
                    if next_offset > offset:
                        segments.append(
                            _Segment(
                                text[offset:next_offset],
                                base_style
                                + Style.from_color(
                                    colors[max(color_indices)].rich_color
                                ),
                            )
                        )
                strips.append(Strip(segments, width))
            else:
                strips.append(Strip([_Segment(text, base_style)], width))

        return StripRenderable(strips, width)
