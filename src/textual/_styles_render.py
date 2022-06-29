from __future__ import annotations

from rich.style import Style
from typing import TYPE_CHECKING

from rich.segment import Segment

from ._border import get_box
from .color import Color
from ._segment_tools import line_crop
from ._types import Lines
from .geometry import Region, Size
from .widget import Widget


if TYPE_CHECKING:
    from .css.styles import RenderStyles


class StylesRenderer:
    def __init__(self, widget: Widget) -> None:
        self._widget = widget
        self._cache: dict[int, list[Segment]] = {}
        self._dirty_lines: set[int] = set()

    def invalidate(self, region: Region) -> None:
        self._dirty_lines.update(region.y_range)

    def render(self, region: Region) -> Lines:

        widget = self._widget
        styles = widget.styles
        size = widget.size
        (base_background, base_color), (background, color) = widget.colors

        return self._render(size, region, styles, base_background, background)

    def _render(
        self,
        size: Size,
        region: Region,
        styles: RenderStyles,
        base_background: Color,
        background: Color,
    ):
        width, height = size
        lines: Lines = []
        add_line = lines.append

        is_dirty = self._dirty_lines.__contains__
        render_line = self.render_line
        for y in region.y_range:
            if is_dirty(y) or y not in self._cache:
                line = render_line(styles, y, size, base_background, background)
                self._cache[y] = line
            else:
                line = self._cache[y]
            add_line(line)
        self._dirty_lines.difference_update(region.y_range)

        if region.x_extents != (0, width):
            _line_crop = line_crop
            x1, x2 = region.x_range
            lines = [_line_crop(line, x1, x2, width) for line in lines]

        return lines

    def render_content_line(self, y: int, width: int) -> list[Segment]:
        return [Segment((str(y) * width)[:width])]

    def render_line(
        self,
        styles: RenderStyles,
        y: int,
        size: Size,
        base_background: Color,
        background: Color,
    ) -> list[Segment]:

        gutter = styles.gutter
        width, height = size
        content_width, content_height = size - gutter.totals
        last_y = height - 1

        pad_top, pad_right, pad_bottom, pad_left = styles.padding
        (
            (border_top, border_top_color),
            (border_right, border_right_color),
            (border_bottom, border_bottom_color),
            (border_left, border_left_color),
        ) = styles.border

        inner_style = Style.from_color(base_background.rich_color)
        outer_style = Style.from_color(background.rich_color)

        if border_top and y in (0, last_y):

            border_color = border_top_color if y == 0 else border_bottom_color
            box_segments = get_box(
                border_top if y == 0 else border_bottom,
                inner_style,
                outer_style,
                Style.from_color(bgcolor=border_color.rich_color),
            )
            box1, box2, box3 = box_segments[0 if y == 0 else 2]

            if border_left and border_right:
                return [box1, Segment(box2.text * (width - 2), box2.style), box3]
            elif border_left:
                return [box1, Segment(box2.text * (width - 1), box2.style)]
            return [Segment(box2.text * (width - 1), box2.style), box3]

        if (pad_top and y < gutter.top) or (pad_bottom and y >= height - gutter.bottom):
            background_style = Style.from_color(bgcolor=base_background.rich_color)
            _, (left, _, _), _ = get_box(
                border_left,
                inner_style,
                outer_style,
                Style.from_color(bgcolor=border_left_color.rich_color),
            )
            _, (_, _, right), _ = get_box(
                border_left,
                inner_style,
                outer_style,
                Style.from_color(bgcolor=border_right_color.rich_color),
            )
            if border_left and border_right:
                return [left, Segment(" " * (width - 2), background_style), right]
            if border_left:
                return [left, Segment(" " * (width - 1), background_style)]
            if border_right:
                return [Segment(" " * (width - 1), background_style), right]
            return [Segment(" " * width, background_style)]

        line_y = y - gutter.top
        line = self.render_content_line(line_y, content_width)

        if pad_left and pad_right:
            line = [
                Segment(" " * pad_left, inner_style),
                *line,
                Segment(" " * pad_right, inner_style),
            ]
        elif pad_left:
            line = [
                Segment(" " * pad_left, inner_style),
                *line,
            ]
        elif pad_right:
            line = [
                *line,
                Segment(" " * pad_right, inner_style),
            ]

        if not border_left and not border_right:
            return line

        _, (left, _, _), _ = get_box(
            border_left,
            inner_style,
            outer_style,
            Style.from_color(border_left_color.rich_color),
        )
        _, (_, _, right), _ = get_box(
            border_left,
            inner_style,
            outer_style,
            Style.from_color(border_right_color.rich_color),
        )

        if border_left and border_right:
            return [left, *line, right]
        elif border_left:
            return [left, *line]

        return [right, *line]


if __name__ == "__main__":

    from rich import print
    from .css.styles import Styles

    styles = Styles()
    styles.padding = 2
    styles.border = ("solid", Color.parse("red"))

    size = Size(40, 10)
    sr = StylesRenderer(None)
    lines = sr._render(
        size, size.region, styles, Color.parse("blue"), Color.parse("green")
    )

    from rich.segment import SegmentLines

    print(SegmentLines(lines, new_lines=True))
