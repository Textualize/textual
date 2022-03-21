from __future__ import annotations

from functools import lru_cache

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
import rich.repr
from rich.segment import Segment, SegmentLines
from rich.style import Style, StyleType

from .css.types import EdgeStyle

INNER = 1
OUTER = 2

BORDER_CHARS: dict[str, tuple[str, str, str]] = {
    "": ("   ", "   ", "   "),
    "none": ("   ", "   ", "   "),
    "round": ("╭─╮", "│ │", "╰─╯"),
    "solid": ("┌─┐", "│ │", "└─┘"),
    "double": ("╔═╗", "║ ║", "╚═╝"),
    "dashed": ("┏╍┓", "╏ ╏", "┗╍┛"),
    "heavy": ("┏━┓", "┃ ┃", "┗━┛"),
    "inner": ("▗▄▖", "▐ ▌", "▝▀▘"),
    "outer": ("▛▀▜", "▌ ▐", "▙▄▟"),
    "hkey": ("▔▔▔", "   ", "▁▁▁"),
    "vkey": ("▏ ▕", "▏ ▕", "▏ ▕"),
    "tall": ("▕▔▏", "▕ ▏", "▕▁▏"),
    "wide": ("▁▁▁", "▏ ▕", "▔▔▔"),
}

BORDER_LOCATIONS: dict[
    str, tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]
] = {
    "": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "none": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "round": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "solid": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "double": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "dashed": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "heavy": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "inner": ((1, 1, 1), (1, 1, 1), (1, 1, 1)),
    "outer": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "hkey": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "vkey": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "tall": ((1, 0, 1), (1, 0, 1), (1, 0, 1)),
    "wide": ((1, 1, 1), (0, 1, 0), (1, 1, 1)),
}


@lru_cache(maxsize=1024)
def get_box(
    name: str, inner_style: Style, outer_style: Style, style: Style
) -> tuple[
    tuple[Segment, Segment, Segment],
    tuple[Segment, Segment, Segment],
    tuple[Segment, Segment, Segment],
]:
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

    styles = (inner_style, outer_style)

    return (
        (
            _Segment(top1, styles[ltop1] + style),
            _Segment(top2, styles[ltop2] + style),
            _Segment(top3, styles[ltop3] + style),
        ),
        (
            _Segment(mid1, styles[lmid1] + style),
            _Segment(mid2, styles[lmid2] + style),
            _Segment(mid3, styles[lmid3] + style),
        ),
        (
            _Segment(bottom1, styles[lbottom1] + style),
            _Segment(bottom2, styles[lbottom2] + style),
            _Segment(bottom3, styles[lbottom3] + style),
        ),
    )


@rich.repr.auto
class Border:
    def __init__(
        self,
        renderable: RenderableType,
        edge_styles: tuple[EdgeStyle, EdgeStyle, EdgeStyle, EdgeStyle],
        outline: bool = False,
        inner_color: Color | None = None,
        outer_color: Color | None = None,
    ):
        self.renderable = renderable
        self.edge_styles = edge_styles
        self.outline = outline

        (
            (top, top_color),
            (right, right_color),
            (bottom, bottom_color),
            (left, left_color),
        ) = edge_styles
        self._sides = (top or "none", right or "none", bottom or "none", left or "none")
        from_color = Style.from_color

        self._styles = (
            from_color(top_color),
            from_color(right_color),
            from_color(bottom_color),
            from_color(left_color),
        )
        self.inner_style = from_color(bgcolor=inner_color)
        self.outer_style = from_color(bgcolor=outer_color)

    def _crop_renderable(self, lines: list[list[Segment]], width: int) -> None:
        """Crops a renderable in place.

        Args:
            lines (list[list[Segment]]): Segment lines.
            width (int): Desired width.
        """
        top, right, bottom, left = self._sides
        has_left = left != "none"
        has_right = right != "none"
        has_top = top != "none"
        has_bottom = bottom != "none"

        if has_top:
            lines.pop(0)
        if has_bottom:
            lines.pop(-1)

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

        has_left = left != "none"
        has_right = right != "none"
        has_top = top != "none"
        has_bottom = bottom != "none"

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
                    render_options = options
                    has_top = has_bottom = False

        lines = console.render_lines(self.renderable, render_options)

        if self.outline:
            self._crop_renderable(lines, options.max_width)

        _Segment = Segment
        new_line = _Segment.line()
        if has_top:
            box1, box2, box3 = get_box(top, style, outer_style, top_style)[0]
            if has_left:
                yield box1 if top == left else _Segment(" ", box2.style)
                # yield _Segment(box1 if top == left else " ", top_style)
            yield _Segment(box2.text * width, box2.style)
            # yield _Segment(box2 * width, top_style)
            if has_right:
                yield box3 if top == left else _Segment(" ", box3.style)
                # yield _Segment(box3 if top == right else " ", top_style)
            yield new_line

        left_segment = get_box(left, style, outer_style, left_style)[1][0]
        _right_segment = get_box(right, style, outer_style, right_style)[1][2]
        right_segment = _Segment(_right_segment.text + "\n", _right_segment.style)
        # box_right = BOX[right][1][2]
        # left_segment = _Segment(box_left, left_style)
        # right_segment = _Segment(box_right + "\n", right_style)
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
            box1, box2, box3 = get_box(top, style, outer_style, bottom_style)[2]
            if has_left:
                yield box1 if bottom == left else _Segment(" ", box1.style)
                # yield _Segment(box1 if bottom == left else " ", bottom_style)
            # yield _Segment(box2 * width, bottom_style)
            yield _Segment(box2.text * width, box2.style)
            if has_right:
                yield box3 if bottom == right else _Segment(" ", box3.style)
                # yield _Segment(box3 if bottom == right else " ", bottom_style)
            yield new_line


if __name__ == "__main__":
    from rich import print
    from rich.color import Color
    from rich.text import Text
    from rich.padding import Padding

    inner = Color.parse("#303F9F")
    outer = Color.parse("#212121")

    lorem = """[#C5CAE9]Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit libero, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum. In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus."""
    text = Text.from_markup(lorem)
    border = Border(
        Padding(text, 1, style="on #303F9F"),
        (
            ("wide", Color.parse("#C5CAE9")),
            ("wide", Color.parse("#C5CAE9")),
            ("wide", Color.parse("#C5CAE9")),
            ("wide", Color.parse("#C5CAE9")),
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
