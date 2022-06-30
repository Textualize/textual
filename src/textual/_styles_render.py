from __future__ import annotations

from rich.style import Style
from typing import Iterable, TYPE_CHECKING

from rich.segment import Segment

from ._border import get_box
from .color import Color
from .css.types import EdgeType
from .renderables.opacity import Opacity
from .renderables.tint import Tint
from ._segment_tools import line_crop
from ._types import Lines
from .geometry import Region, Size


if TYPE_CHECKING:
    from .css.styles import RenderStyles
    from .widget import Widget


NORMALIZE_BORDER: dict[EdgeType, EdgeType] = {"none": "", "hidden": ""}


class StylesRenderer:
    """Responsible for rendering CSS Styles and keeping a cached of rendered lines."""

    def __init__(self, widget: Widget) -> None:
        self._widget = widget
        self._cache: dict[int, list[Segment]] = {}
        self._dirty_lines: set[int] = set()

    def set_dirty(self, *regions: Region) -> None:
        """Add a dirty region, or set the entire widget as dirty."""
        if regions:
            for region in regions:
                self._dirty_lines.update(region.line_range)
        else:
            self._dirty_lines.clear()
            self._dirty_lines.update(self._widget.size.lines_range)

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
        simplify = Segment.simplify

        is_dirty = self._dirty_lines.__contains__
        render_line = self.render_line
        for y in region.line_range:
            if is_dirty(y) or y not in self._cache:
                line = render_line(styles, y, size, base_background, background)
                line = list(simplify(line))
                self._cache[y] = line
            else:
                line = self._cache[y]
            add_line(line)
        self._dirty_lines.difference_update(region.line_range)

        if region.column_span != (0, width):
            _line_crop = line_crop
            x1, x2 = region.column_span
            lines = [_line_crop(line, x1, x2, width) for line in lines]

        return lines

    def render_content_line(self, y: int) -> list[Segment]:
        return self._widget.render_line(y)

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

        pad_top, pad_right, pad_bottom, pad_left = styles.padding
        (
            (border_top, border_top_color),
            (border_right, border_right_color),
            (border_bottom, border_bottom_color),
            (border_left, border_left_color),
        ) = styles.border

        normalize_border_get = NORMALIZE_BORDER.get
        border_top = normalize_border_get(border_top, border_top)
        border_right = normalize_border_get(border_right, border_right)
        border_bottom = normalize_border_get(border_bottom, border_bottom)
        border_left = normalize_border_get(border_left, border_left)

        from_color = Style.from_color

        rich_style = styles.rich_style
        inner_style = from_color(bgcolor=background.rich_color) + rich_style
        outer_style = from_color(bgcolor=base_background.rich_color)

        def post(segments: Iterable[Segment]) -> list[Segment]:
            if styles.opacity != 1.0:
                segments = Opacity.process_segments(segments, styles.opacity)
            if styles.tint.a:
                segments = Tint.process_segments(segments, styles.tint)
            return segments if isinstance(segments, list) else list(segments)

        # Draw top or bottom borders
        if border_top and y in (0, height - 1):

            border_color = border_top_color if y == 0 else border_bottom_color
            box_segments = get_box(
                border_top if y == 0 else border_bottom,
                inner_style,
                outer_style,
                from_color(color=border_color.rich_color),
            )
            box1, box2, box3 = box_segments[0 if y == 0 else 2]

            if border_left and border_right:
                return post([box1, Segment(box2.text * (width - 2), box2.style), box3])
            elif border_left:
                return post([box1, Segment(box2.text * (width - 1), box2.style)])
            elif border_right:
                return post([Segment(box2.text * (width - 1), box2.style), box3])
            else:
                return post([Segment(box2.text * width, box2.style)])

        # Draw padding
        if (pad_top and y < gutter.top) or (pad_bottom and y >= height - gutter.bottom):
            background_style = from_color(
                color=rich_style.color, bgcolor=background.rich_color
            )
            _, (left, _, _), _ = get_box(
                border_left,
                inner_style,
                outer_style,
                from_color(color=border_left_color.rich_color),
            )
            _, (_, _, right), _ = get_box(
                border_right,
                inner_style,
                outer_style,
                from_color(color=border_right_color.rich_color),
            )
            if border_left and border_right:
                return post([left, Segment(" " * (width - 2), background_style), right])
            if border_left:
                return post([left, Segment(" " * (width - 1), background_style)])
            if border_right:
                return post([Segment(" " * (width - 1), background_style), right])
            return post([Segment(" " * width, background_style)])

        # Apply background style
        line = self.render_content_line(y - gutter.top)
        if inner_style:
            line = list(Segment.apply_style(line, inner_style))

        # Add padding
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
            return post(line)

        # Add left / right border
        _, (left, _, _), _ = get_box(
            border_left,
            inner_style,
            outer_style,
            from_color(border_left_color.rich_color),
        )
        _, (_, _, right), _ = get_box(
            border_right,
            inner_style,
            outer_style,
            from_color(border_right_color.rich_color),
        )

        if border_left and border_right:
            return post([left, *line, right])
        elif border_left:
            return post([left, *line])

        return post([*line, right])


if __name__ == "__main__":

    from rich import print
    from .css.styles import Styles

    styles = Styles()
    styles.padding = 2
    styles.border = (
        ("tall", Color.parse("red")),
        ("none", Color.parse("white")),
        ("outer", Color.parse("red")),
        ("none", Color.parse("red")),
    )

    size = Size(40, 10)
    sr = StylesRenderer(None)
    lines = sr._render(
        size, size.region, styles, Color.parse("blue"), Color.parse("green")
    )
    for line in lines:
        print(line)
    from rich.segment import SegmentLines

    print(SegmentLines(lines, new_lines=True))
