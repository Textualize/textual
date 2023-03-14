from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Tuple, cast

from rich.console import Console
from rich.segment import Segment
from rich.style import Style
from rich.text import Text

from .color import Color
from .css.types import AlignHorizontal, EdgeStyle, EdgeType

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

INNER = 1
OUTER = 2

BORDER_CHARS: dict[
    EdgeType, tuple[tuple[str, str, str], tuple[str, str, str], tuple[str, str, str]]
] = {
    # Three tuples for the top, middle, and bottom rows.
    # The sub-tuples are the characters for the left, center, and right borders.
    "": (
        (" ", " ", " "),
        (" ", " ", " "),
        (" ", " ", " "),
    ),
    "ascii": (
        ("+", "-", "+"),
        ("|", " ", "|"),
        ("+", "-", "+"),
    ),
    "none": (
        (" ", " ", " "),
        (" ", " ", " "),
        (" ", " ", " "),
    ),
    "hidden": (
        (" ", " ", " "),
        (" ", " ", " "),
        (" ", " ", " "),
    ),
    "blank": (
        (" ", " ", " "),
        (" ", " ", " "),
        (" ", " ", " "),
    ),
    "round": (
        ("╭", "─", "╮"),
        ("│", " ", "│"),
        ("╰", "─", "╯"),
    ),
    "solid": (
        ("┌", "─", "┐"),
        ("│", " ", "│"),
        ("└", "─", "┘"),
    ),
    "double": (
        ("╔", "═", "╗"),
        ("║", " ", "║"),
        ("╚", "═", "╝"),
    ),
    "dashed": (
        ("┏", "╍", "┓"),
        ("╏", " ", "╏"),
        ("┗", "╍", "┛"),
    ),
    "heavy": (
        ("┏", "━", "┓"),
        ("┃", " ", "┃"),
        ("┗", "━", "┛"),
    ),
    "inner": (
        ("▗", "▄", "▖"),
        ("▐", " ", "▌"),
        ("▝", "▀", "▘"),
    ),
    "outer": (
        ("▛", "▀", "▜"),
        ("▌", " ", "▐"),
        ("▙", "▄", "▟"),
    ),
    "hkey": (
        ("▔", "▔", "▔"),
        (" ", " ", " "),
        ("▁", "▁", "▁"),
    ),
    "vkey": (
        ("▏", " ", "▕"),
        ("▏", " ", "▕"),
        ("▏", " ", "▕"),
    ),
    "tall": (
        ("▊", "▔", "▎"),
        ("▊", " ", "▎"),
        ("▊", "▁", "▎"),
    ),
    "wide": (
        ("▁", "▁", "▁"),
        ("▎", " ", "▋"),
        ("▔", "▔", "▔"),
    ),
}

# Some of the borders are on the widget background and some are on the background of the parent
# This table selects which for each character, 0 indicates the widget, 1 selects the parent.
# 2 and 3 reverse a cross-combination of the background and foreground colors of 0 and 1.
BORDER_LOCATIONS: dict[
    EdgeType, tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]
] = {
    "": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "ascii": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "none": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "hidden": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "blank": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "round": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "solid": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "double": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "dashed": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "heavy": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "inner": (
        (1, 1, 1),
        (1, 1, 1),
        (1, 1, 1),
    ),
    "outer": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "hkey": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "vkey": (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    "tall": (
        (2, 0, 1),
        (2, 0, 1),
        (2, 0, 1),
    ),
    "wide": (
        (1, 1, 1),
        (0, 1, 3),
        (1, 1, 1),
    ),
}

# In a similar fashion, we extract the border _label_ locations for easier access when
# rendering a border label.
# The values are a pair with (title location, subtitle location).
BORDER_LABEL_LOCATIONS: dict[EdgeType, tuple[int, int]] = {
    edge_type: (locations[0][1], locations[2][1])
    for edge_type, locations in BORDER_LOCATIONS.items()
}

INVISIBLE_EDGE_TYPES = cast("frozenset[EdgeType]", frozenset(("", "none", "hidden")))

BorderValue: TypeAlias = Tuple[EdgeType, Color]

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
        name: Name of the box type.
        inner_style: The inner style (widget background)
        outer_style: The outer style (parent background)
        style: Widget style

    Returns:
        A tuple of 3 Segment triplets.
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


@lru_cache(maxsize=1024)
def render_border_label(
    label: str,
    is_title: bool,
    name: EdgeType,
    width: int,
    inner_style: Style,
    outer_style: Style,
    style: Style,
) -> Segment:
    """Render a border label (the title or subtitle) with optional markup.

    The styling that may be embedded in the label will be reapplied after taking into
    account the inner, outer, and border-specific styles.

    Args:
        label: The label to display (that may contain markup).
        is_title: Whether we are rendering the title (`True`) or the subtitle (`False`).
        name: Name of the box type.
        width: The width, in cells, of the space available for the whole edge.
            This accounts for the 2 cells made available for the corner, which means
            that the space available for the label is effectively `width - 2`.
        inner_style: The inner style (widget background).
        outer_style: The outer style (parent background).
        style: Widget style.
    """
    if not label:
        return Segment("", Style())

    console = Console(width=width - 2)
    text_label = Text.from_markup(label)
    wrapped = text_label.wrap(console, console.width, overflow="ellipsis", no_wrap=True)
    segment_label = next(segment for segment in console.render(wrapped))

    label_style_location = BORDER_LABEL_LOCATIONS[name][0 if is_title else 1]

    inner = inner_style + style
    outer = outer_style + style
    segment_style: Style
    if label_style_location == 0:
        segment_style = inner + segment_label.style
    elif label_style_location == 1:
        segment_style = outer + segment_label.style
    elif label_style_location == 2:
        segment_style = (
            Style.from_color(outer.bgcolor, inner.color) + segment_label.style
        )
    elif label_style_location == 3:
        segment_style = (
            Style.from_color(inner.bgcolor, outer.color) + segment_label.style
        )
    else:
        assert False

    return Segment(segment_label.text, segment_style)


def render_row(
    box_row: tuple[Segment, Segment, Segment],
    width: int,
    left: bool,
    right: bool,
    label: Segment,
    label_alignment: AlignHorizontal,
) -> list[Segment]:
    """Render a top, or bottom border row.

    Args:
        box_row: Corners and side segments.
        width: Total width of resulting line.
        left: Render left corner.
        right: Render right corner.

    Returns:
        A list of segments.
    """
    box1, box2, box3 = box_row

    corners_needed = left + right
    label_length = label.cell_length
    space_available = max(0, width - corners_needed - label_length)

    middle_segments: list[Segment]
    if not space_available:
        middle_segments = [label]
    elif label_alignment == "left" or label_alignment == "right":
        edge = Segment(box2.text * space_available, box2.style)
        middle_segments = [label, edge] if label_alignment == "left" else [edge, label]
    elif label_alignment == "center":
        length_on_left = space_available // 2
        length_on_right = space_available - length_on_left
        middle_segments = [
            Segment(box2.text * length_on_left, box2.style),
            label,
            Segment(box2.text * length_on_right, box2.style),
        ]
    else:
        assert False

    if left and right:
        return [box1] + middle_segments + [box3]
    if left:
        return [box1] + middle_segments
    if right:
        return middle_segments + [box3]
    else:
        return middle_segments


_edge_type_normalization_table: dict[EdgeType, EdgeType] = {
    # i.e. we normalize "border: none;" to "border: ;".
    # As a result our layout-related calculations that include borders are simpler (and have better performance)
    "none": "",
    "hidden": "",
}


def normalize_border_value(value: BorderValue) -> BorderValue:
    return _edge_type_normalization_table.get(value[0], value[0]), value[1]
