from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.segment import Segment
from rich.style import Style

from .css.types import EdgeStyle

from ._box import BOX_STYLES


class Border:
    def __init__(
        self,
        renderable: RenderableType,
        edge_styles: tuple[EdgeStyle, EdgeStyle, EdgeStyle, EdgeStyle],
    ):
        self.renderable = renderable
        self.edge_styles = edge_styles

    @property
    def sides(self) -> tuple[str, str, str, str]:
        (top, _), (right, _), (bottom, _), (left, _) = self.edge_styles
        return (top or "none", right or "none", bottom or "none", left or "none")

    @property
    def styles(self) -> tuple[Style, Style, Style, Style]:
        (_, top), (_, right), (_, left), (_, bottom) = self.edge_styles
        return (top, right, left, bottom)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        top, right, bottom, left = self.sides
        top_style, right_style, bottom_style, left_style = self.styles
        BOX = BOX_STYLES

        has_left = left != "none"
        has_right = right != "none"
        has_top = top != "none"
        has_bottom = bottom != "none"

        width = options.max_width - has_left - has_right
        if options.height is None:
            render_options = options.update_width(width)
        else:
            height = options.height - has_top - has_bottom
            render_options = options.update_dimensions(width, height)

        lines = console.render_lines(self.renderable, render_options)

        _Segment = Segment
        new_line = _Segment.line()
        if has_top:
            box1, box2, box3 = iter(BOX[top][0])
            if has_left:
                yield _Segment(box1 if top == left else " ", top_style)
            yield _Segment(box2 * width, top_style)
            if has_right:
                yield _Segment(box3 if top == right else " ", top_style)
            yield new_line

        box_left = BOX[left][1][0]
        box_right = BOX[right][1][2]
        left_segment = _Segment(box_left, left_style)
        right_segment = _Segment(box_right, right_style)
        if has_left and has_right:
            for line in lines:
                yield left_segment
                yield from line
                yield right_segment
                yield new_line
        elif has_left:
            for line in lines:
                yield left_segment
                yield from line
                yield new_line
        elif has_right:
            for line in lines:
                yield from line
                yield right_segment
                yield new_line
        else:
            for line in lines:
                yield from line
                yield new_line

        if has_bottom:
            box1, box2, box3 = iter(BOX[bottom][2])
            if has_left:
                yield _Segment(box1 if bottom == left else " ", bottom_style)
            yield _Segment(box2 * width, bottom_style)
            if has_right:
                yield _Segment(box3 if bottom == right else " ", bottom_style)
            yield new_line


if __name__ == "__main__":
    from rich import print
    from rich.text import Text

    text = Text("Textual " * 40, style="dim")
    print(
        Border(
            text,
            (
                ("outer", Style.parse("green on red")),
                ("none", Style.parse("green")),
                ("double", Style.parse("green")),
                ("double", Style.parse("green")),
            ),
        )
    )
