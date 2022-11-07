from __future__ import annotations

from functools import lru_cache
from typing import cast, Tuple, Union

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
import rich.repr
from rich.segment import Segment, SegmentLines
from rich.style import Style

from .color import Color
from .css.types import EdgeStyle, EdgeType
from ._typing import TypeAlias

INNER = 1
OUTER = 2

BORDER_CHARS: dict[EdgeType, tuple[str, str, str]] = {
    # Each string of the tuple represents a sub-tuple itself:
    #  - 1st string represents (top1, top2, top3)
    #  - 2nd string represents (mid1, mid2, mid3)
    #  - 3rd string represents (bottom1, bottom2, bottom3)
    "": ("   ", "   ", "   "),
    "ascii": ("+-+", "| |", "+-+"),
    "none": ("   ", "   ", "   "),
    "hidden": ("   ", "   ", "   "),
    "blank": ("   ", "   ", "   "),
    "round": ("╭─╮", "│ │", "╰─╯"),
    "solid": ("┌─┐", "│ │", "└─┘"),
    "double": ("╔═╗", "║ ║", "╚═╝"),
    "dashed": ("┏╍┓", "╏ ╏", "┗╍┛"),
    "heavy": ("┏━┓", "┃ ┃", "┗━┛"),
    "inner": ("▗▄▖", "▐ ▌", "▝▀▘"),
    "outer": ("▛▀▜", "▌ ▐", "▙▄▟"),
    "hkey": ("▔▔▔", "   ", "▁▁▁"),
    "vkey": ("▏ ▕", "▏ ▕", "▏ ▕"),
    "tall": ("▊▔▎", "▊ ▎", "▊▁▎"),
    "wide": ("▁▁▁", "▎ ▋", "▔▔▔"),
}

# Some of the borders are on the widget background and some are on the background of the parent
# This table selects which for each character, 0 indicates the widget, 1 selects the parent
BORDER_LOCATIONS: dict[
    EdgeType, tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]
] = {
    "": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "ascii": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "none": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "hidden": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "blank": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "round": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "solid": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "double": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "dashed": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "heavy": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "inner": ((1, 1, 1), (1, 1, 1), (1, 1, 1)),
    "outer": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "hkey": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "vkey": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "tall": ((2, 0, 1), (2, 0, 1), (2, 0, 1)),
    "wide": ((1, 1, 1), (0, 1, 3), (1, 1, 1)),
}

INVISIBLE_EDGE_TYPES = cast("frozenset[EdgeType]", frozenset(("", "none", "hidden")))

BorderValue: TypeAlias = Tuple[EdgeType, Union[str, Color, Style]]

BoxSegments: TypeAlias = Tuple[
    Tuple[Segment, Segment, Segment],
    Tuple[Segment, Segment, Segment],
    Tuple[Segment, Segment, Segment],
]

Borders: TypeAlias = Tuple[EdgeStyle, EdgeStyle, EdgeStyle, EdgeStyle]


@lru_cache(maxsize=1024)
def get_box(
    name: EdgeType,
    inner_style: Style,
    outer_style: Style,
    style: Style,
) -> BoxSegments:
    """Get segments used to render a box.

    Args:
        name (str): Name of the box type.
        inner_style (Style): The inner style (widget background)
        outer_style (Style): The outer style (parent background)
        style (Style): Widget style

    Returns:
        tuple: A tuple of 3 Segment triplets.
    """
    _Segment = Segment
    (
        (top1, top2, top3),
        (mid1, mid2, mid3),
        (bottom1, bottom2, bottom3),
    ) = BORDER_CHARS[name]

    (
        (ltop1, ltop2, ltop3),
        (lmid1, lmid2, lmid3),
        (lbottom1, lbottom2, lbottom3),
    ) = BORDER_LOCATIONS[name]

    inner = inner_style + style
    outer = outer_style + style
    styles = (
        inner,
        outer,
        Style.from_color(outer.bgcolor, inner.color),
        Style.from_color(inner.bgcolor, outer.color),
    )

    return (
        (
            _Segment(top1, styles[ltop1]),
            _Segment(top2, styles[ltop2]),
            _Segment(top3, styles[ltop3]),
        ),
        (
            _Segment(mid1, styles[lmid1]),
            _Segment(mid2, styles[lmid2]),
            _Segment(mid3, styles[lmid3]),
        ),
        (
            _Segment(bottom1, styles[lbottom1]),
            _Segment(bottom2, styles[lbottom2]),
            _Segment(bottom3, styles[lbottom3]),
        ),
    )


def render_row(
    box_row: tuple[Segment, Segment, Segment], width: int, left: bool, right: bool
) -> list[Segment]:
    """Render a top, or bottom border row.

    Args:
        box_row (tuple[Segment, Segment, Segment]): Corners and side segments.
        width (int): Total width of resulting line.
        left (bool): Render left corner.
        right (bool): Render right corner.

    Returns:
        list[Segment]: A list of segments.
    """
    box1, box2, box3 = box_row
    if left and right:
        return [box1, Segment(box2.text * (width - 2), box2.style), box3]
    if left:
        return [box1, Segment(box2.text * (width - 1), box2.style)]
    if right:
        return [Segment(box2.text * (width - 1), box2.style), box3]
    else:
        return [Segment(box2.text * width, box2.style)]


@rich.repr.auto
class Border:
    """Renders Textual CSS borders.

    This is analogous to Rich's `Box` but more flexible. Different borders may be
    applied to each of the four edges, and more advanced borders can be achieved through
    various combinations of Widget and parent background colors.

    """

    def __init__(
        self,
        renderable: RenderableType,
        borders: Borders,
        inner_color: Color,
        outer_color: Color,
        outline: bool = False,
    ):
        self.renderable = renderable
        self.edge_styles = borders
        self.outline = outline

        (
            (top, top_color),
            (right, right_color),
            (bottom, bottom_color),
            (left, left_color),
        ) = borders
        self._sides: tuple[EdgeType, EdgeType, EdgeType, EdgeType]
        self._sides = (top, right, bottom, left)
        from_color = Style.from_color

        self._styles = (
            from_color(top_color.rich_color),
            from_color(right_color.rich_color),
            from_color(bottom_color.rich_color),
            from_color(left_color.rich_color),
        )
        self.inner_style = from_color(bgcolor=inner_color.rich_color)
        self.outer_style = from_color(bgcolor=outer_color.rich_color)

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.renderable
        yield self.edge_styles

    def _crop_renderable(self, lines: list[list[Segment]], width: int) -> None:
        """Crops a renderable in place.

        Args:
            lines (list[list[Segment]]): Segment lines.
            width (int): Desired width.
        """
        top, right, bottom, left = self._sides
        # the 4 following lines rely on the fact that we normalise "none" and "hidden" to en empty string
        has_left = bool(left)
        has_right = bool(right)
        has_top = bool(top)
        has_bottom = bool(bottom)

        if has_top:
            lines.pop(0)
        if has_bottom and lines:
            lines.pop(-1)

        # TODO: Divide is probably quite inefficient here,
        # It could be much faster for the specific case of one off the start end end
        divide = Segment.divide
        if has_left and has_right:
            for line in lines:
                _, line[:] = divide(line, [1, width - 1])
        elif has_left:
            for line in lines:
                _, line[:] = divide(line, [1, width])
        elif has_right:
            for line in lines:
                line[:], _ = divide(line, [width - 1, width])

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        top, right, bottom, left = self._sides
        style = console.get_style(self.inner_style)
        outer_style = console.get_style(self.outer_style)
        top_style, right_style, bottom_style, left_style = self._styles

        # ditto than in `_crop_renderable` ☝
        has_left = bool(left)
        has_right = bool(right)
        has_top = bool(top)
        has_bottom = bool(bottom)

        width = options.max_width - has_left - has_right

        if width <= 2:
            lines = console.render_lines(self.renderable, options, new_lines=True)
            yield SegmentLines(lines)
            return

        if self.outline:
            render_options = options
        else:
            if options.height is None:
                render_options = options.update_width(width)
            else:
                new_height = options.height - has_top - has_bottom
                if new_height >= 1:
                    render_options = options.update_dimensions(width, new_height)
                else:
                    render_options = options.update_width(width)

        lines = console.render_lines(self.renderable, render_options)
        if self.outline:
            self._crop_renderable(lines, options.max_width)

        _Segment = Segment
        new_line = _Segment.line()
        if has_top:
            box1, box2, box3 = get_box(top, style, outer_style, top_style)[0]
            if has_left:
                yield box1 if top == left else _Segment(" ", box2.style)
            yield _Segment(box2.text * width, box2.style)
            if has_right:
                yield box3 if top == left else _Segment(" ", box3.style)
            yield new_line

        left_segment = get_box(left, style, outer_style, left_style)[1][0]
        _right_segment = get_box(right, style, outer_style, right_style)[1][2]
        right_segment = _Segment(_right_segment.text + "\n", _right_segment.style)

        if has_left and has_right:
            for line in lines:
                yield left_segment
                yield from line
                yield right_segment
        elif has_left:
            for line in lines:
                yield left_segment
                yield from line
                yield new_line
        elif has_right:
            for line in lines:
                yield from line
                yield right_segment
        else:
            for line in lines:
                yield from line
                yield new_line

        if has_bottom:
            box1, box2, box3 = get_box(bottom, style, outer_style, bottom_style)[2]
            if has_left:
                yield box1 if bottom == left else _Segment(" ", box1.style)
            yield _Segment(box2.text * width, box2.style)
            if has_right:
                yield box3 if bottom == right else _Segment(" ", box3.style)
            yield new_line


_edge_type_normalization_table: dict[EdgeType, EdgeType] = {
    # i.e. we normalize "border: none;" to "border: ;".
    # As a result our layout-related calculations that include borders are simpler (and have better performance)
    "none": "",
    "hidden": "",
}


def normalize_border_value(value: BorderValue) -> BorderValue:
    return _edge_type_normalization_table.get(value[0], value[0]), value[1]


if __name__ == "__main__":
    from rich import print
    from rich.text import Text
    from rich.padding import Padding

    from .color import Color

    inner = Color.parse("#303F9F")
    outer = Color.parse("#212121")

    lorem = """[#C5CAE9]Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit libero, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum. In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus."""
    text = Text.from_markup(lorem)
    border = Border(
        Padding(text, 1, style="on #303F9F"),
        (
            ("none", Color.parse("#C5CAE9")),
            ("none", Color.parse("#C5CAE9")),
            ("wide", Color.parse("#C5CAE9")),
            ("none", Color.parse("#C5CAE9")),
        ),
        inner_color=inner,
        outer_color=outer,
    )

    print(
        Padding(border, (1, 2), style="on #212121"),
    )
    print()

    border = Border(
        Padding(text, 1, style="on #303F9F"),
        (
            ("hkey", Color.parse("#8BC34A")),
            ("hkey", Color.parse("#8BC34A")),
            ("hkey", Color.parse("#8BC34A")),
            ("hkey", Color.parse("#8BC34A")),
        ),
        inner_color=inner,
        outer_color=outer,
    )

    print(
        Padding(border, (1, 2), style="on #212121"),
    )
