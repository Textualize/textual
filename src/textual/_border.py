from __future__ import annotations

from functools import lru_cache
from typing import cast, Tuple, Union

from rich.segment import Segment
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


_edge_type_normalization_table: dict[EdgeType, EdgeType] = {
    # i.e. we normalize "border: none;" to "border: ;".
    # As a result our layout-related calculations that include borders are simpler (and have better performance)
    "none": "",
    "hidden": "",
}


def normalize_border_value(value: BorderValue) -> BorderValue:
    return _edge_type_normalization_table.get(value[0], value[0]), value[1]
