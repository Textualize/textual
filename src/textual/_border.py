from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Iterable, Tuple, cast

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

_EMPTY_SEGMENT = Segment("", Style())

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


def render_border_label(
    label: str,
    is_title: bool,
    name: EdgeType,
    width: int,
    inner_style: Style,
    outer_style: Style,
    style: Style,
    console: Console,
    has_left_corner: bool,
    has_right_corner: bool,
) -> Iterable[Segment]:
    """Render a border label (the title or subtitle) with optional markup.

    The styling that may be embedded in the label will be reapplied after taking into
    account the inner, outer, and border-specific, styles.

    Args:
        label: The label to display (that may contain markup).
        is_title: Whether we are rendering the title (`True`) or the subtitle (`False`).
        name: Name of the box type.
        width: The width, in cells, of the space available for the whole edge.
            This is the total space that may also be needed for the border corners and
            the whitespace padding around the (sub)title. Thus, the effective space
            available for the border label is:
            - `width` if no corner is needed;
            - `width - 2` if one corner is needed; and
            - `width - 4` if both corners are needed.
        inner_style: The inner style (widget background).
        outer_style: The outer style (parent background).
        style: Widget style.
        console: The console that will render the markup in the label.
        has_left_corner: Whether the border edge will have to render a left corner.
        has_right_corner: Whether the border edge will have to render a right corner.

    Returns:
        A list of segments that represent the full label and surrounding padding.
    """
    # How many cells do we need to reserve for surrounding blanks and corners?
    corners_needed = has_left_corner + has_right_corner
    cells_reserved = 2 * corners_needed
    if not label or width <= cells_reserved:
        return

    text_label = Text.from_markup(label)
    text_label.truncate(width - cells_reserved, overflow="ellipsis")
    segments = text_label.render(console)

    label_style_location = BORDER_LABEL_LOCATIONS[name][0 if is_title else 1]

    inner = inner_style + style
    outer = outer_style + style

    base_style: Style
    if label_style_location == 0:
        base_style = inner
    elif label_style_location == 1:
        base_style = outer
    elif label_style_location == 2:
        base_style = Style.from_color(outer.bgcolor, inner.color)
    elif label_style_location == 3:
        base_style = Style.from_color(inner.bgcolor, outer.color)
    else:
        assert False

    styled_segments = [
        Segment(segment.text, base_style + segment.style) for segment in segments
    ]
    blank = Segment(" ", base_style)
    if has_left_corner:
        yield blank
    yield from styled_segments
    if has_right_corner:
        yield blank


def render_row(
    box_row: tuple[Segment, Segment, Segment],
    width: int,
    left: bool,
    right: bool,
    label_segments: Iterable[Segment],
    label_alignment: AlignHorizontal = "left",
) -> Iterable[Segment]:
    """Compose a box row with its padded label.

    This is the function that actually does the work that `render_row` is intended
    to do, but we have many lists of segments flowing around, so it becomes easier
    to yield the segments bit by bit, and the aggregate everything into a list later.

    Args:
        box_row: Corners and side segments.
        width: Total width of resulting line.
        left: Render left corner.
        right: Render right corner.
        label_segments: The segments that make up the label.
        label_alignment: Where to horizontally align the label.

    Returns:
        An iterable of segments.
    """
    box1, box2, box3 = box_row

    corners_needed = left + right
    label_segments_list = list(label_segments)

    label_length = sum((segment.cell_length for segment in label_segments_list), 0)
    space_available = max(0, width - corners_needed - label_length)

    if left:
        yield box1

    if not space_available:
        yield from label_segments_list
    elif not label_length:
        yield Segment(box2.text * space_available, box2.style)
    elif label_alignment == "left" or label_alignment == "right":
        edge = Segment(box2.text * space_available, box2.style)
        if label_alignment == "left":
            yield from label_segments_list
            yield edge
        else:
            yield edge
            yield from label_segments_list
    elif label_alignment == "center":
        length_on_left = space_available // 2
        length_on_right = space_available - length_on_left
        yield Segment(box2.text * length_on_left, box2.style)
        yield from label_segments_list
        yield Segment(box2.text * length_on_right, box2.style)
    else:
        assert False

    if right:
        yield box3


_edge_type_normalization_table: dict[EdgeType, EdgeType] = {
    # i.e. we normalize "border: none;" to "border: ;".
    # As a result our layout-related calculations that include borders are simpler (and have better performance)
    "none": "",
    "hidden": "",
}


def normalize_border_value(value: BorderValue) -> BorderValue:
    return _edge_type_normalization_table.get(value[0], value[0]), value[1]
