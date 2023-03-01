from __future__ import annotations

from functools import lru_cache
from sys import intern
from typing import TYPE_CHECKING, Callable, Iterable

from rich.segment import Segment
from rich.style import Style

from ._border import get_box, render_row
from ._opacity import _apply_opacity
from ._segment_tools import line_pad, line_trim
from .color import Color
from .filter import LineFilter
from .geometry import Region, Size, Spacing
from .renderables.text_opacity import TextOpacity
from .renderables.tint import Tint
from .strip import Strip

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from .css.styles import StylesBase
    from .widget import Widget

RenderLineCallback: TypeAlias = Callable[[int], Strip]


@lru_cache(1024 * 8)
def make_blank(width, style: Style) -> Segment:
    """Make a blank segment.

    Args:
        width: Width of blank.
        style: Style of blank.

    Returns:
        A single segment
    """
    return Segment(intern(" " * width), style)


class StylesCache:
    """Responsible for rendering CSS Styles and keeping a cache of rendered lines.

    The render method applies border, outline, and padding set in the Styles object to widget content.

    The diagram below shows content (possibly from a Rich renderable) with padding and border. The
    labels A. B. and C. indicate the code path (see comments in render_line below) chosen to render
    the indicated lines.

    ```
    ┏━━━━━━━━━━━━━━━━━━━━━━┓◀── A. border
    ┃                      ┃◀┐
    ┃                      ┃ └─ B. border + padding +
    ┃   Lorem ipsum dolor  ┃◀┐         border
    ┃   sit amet,          ┃ │
    ┃   consectetur        ┃ └─ C. border + padding +
    ┃   adipiscing elit,   ┃     content + padding +
    ┃   sed do eiusmod     ┃           border
    ┃   tempor incididunt  ┃
    ┃                      ┃
    ┃                      ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━┛
    ```

    """

    def __init__(self) -> None:
        self._cache: dict[int, Strip] = {}
        self._dirty_lines: set[int] = set()
        self._width = 1

    def set_dirty(self, *regions: Region) -> None:
        """Add a dirty regions."""
        if regions:
            for region in regions:
                self._dirty_lines.update(region.line_range)
        else:
            self.clear()

    def is_dirty(self, y: int) -> bool:
        """Check if a given line is dirty (needs to be rendered again).

        Args:
            y: Y coordinate of line.

        Returns:
            True if line requires a render, False if can be cached.
        """
        return y in self._dirty_lines

    def clear(self) -> None:
        """Clear the styles cache (will cause the content to re-render)."""
        self._cache.clear()
        self._dirty_lines.clear()

    def render_widget(self, widget: Widget, crop: Region) -> list[Strip]:
        """Render the content for a widget.

        Args:
            widget: A widget.
            region: A region of the widget to render.

        Returns:
            Rendered lines.
        """
        base_background, background = widget.background_colors
        styles = widget.styles
        strips = self.render(
            styles,
            widget.region.size,
            base_background,
            background,
            widget.render_line,
            content_size=widget.content_region.size,
            padding=styles.padding,
            crop=crop,
            filter=widget.app._filter,
        )
        if widget.auto_links:
            hover_style = widget.hover_style
            if (
                hover_style._link_id
                and hover_style._meta
                and "@click" in hover_style.meta
            ):
                link_hover_style = widget.link_hover_style
                if link_hover_style:
                    strips = [
                        strip.style_links(hover_style.link_id, link_hover_style)
                        for strip in strips
                    ]

        return strips

    def render(
        self,
        styles: StylesBase,
        size: Size,
        base_background: Color,
        background: Color,
        render_content_line: RenderLineCallback,
        content_size: Size | None = None,
        padding: Spacing | None = None,
        crop: Region | None = None,
        filter: LineFilter | None = None,
    ) -> list[Strip]:
        """Render a widget content plus CSS styles.

        Args:
            styles: CSS Styles object.
            size: Size of widget.
            base_background: Background color beneath widget.
            background: Background color of widget.
            render_content_line: Callback to render content line.
            content_size: Size of content or None to assume full size. Defaults to None.
            padding: Override padding from Styles, or None to use styles.padding. Defaults to None.
            crop: Region to crop to. Defaults to None.

        Returns:
            Rendered lines.
        """
        if content_size is None:
            content_size = size
        if padding is None:
            padding = styles.padding
        if crop is None:
            crop = size.region

        width, _height = size
        if width != self._width:
            self.clear()
            self._width = width
        strips: list[Strip] = []
        add_strip = strips.append

        is_dirty = self._dirty_lines.__contains__
        render_line = self.render_line
        for y in crop.line_range:
            if is_dirty(y) or y not in self._cache:
                strip = render_line(
                    styles,
                    y,
                    size,
                    content_size,
                    padding,
                    base_background,
                    background,
                    render_content_line,
                )
                self._cache[y] = strip
            else:
                strip = self._cache[y]
            if filter:
                strip = strip.apply_filter(filter)
            add_strip(strip)
        self._dirty_lines.difference_update(crop.line_range)

        if crop.column_span != (0, width):
            x1, x2 = crop.column_span
            strips = [strip.crop(x1, x2) for strip in strips]

        return strips

    def render_line(
        self,
        styles: StylesBase,
        y: int,
        size: Size,
        content_size: Size,
        padding: Spacing,
        base_background: Color,
        background: Color,
        render_content_line: Callable[[int], Strip],
    ) -> Strip:
        """Render a styled line.

        Args:
            styles: Styles object.
            y: The y coordinate of the line (relative to widget screen offset).
            size: Size of the widget.
            content_size: Size of the content area.
            padding: Padding.
            base_background: Background color of widget beneath this line.
            background: Background color of widget.
            render_content_line: Callback to render a line of content.

        Returns:
            A line of segments.
        """

        gutter = styles.gutter
        width, height = size
        content_width, content_height = content_size

        pad_top, pad_right, pad_bottom, pad_left = padding

        (
            (border_top, border_top_color),
            (border_right, border_right_color),
            (border_bottom, border_bottom_color),
            (border_left, border_left_color),
        ) = styles.border

        (
            (outline_top, outline_top_color),
            (outline_right, outline_right_color),
            (outline_bottom, outline_bottom_color),
            (outline_left, outline_left_color),
        ) = styles.outline

        from_color = Style.from_color

        inner = from_color(bgcolor=(base_background + background).rich_color)
        outer = from_color(bgcolor=base_background.rich_color)

        def post(segments: Iterable[Segment]) -> Iterable[Segment]:
            """Post process segments to apply opacity and tint.

            Args:
                segments: Iterable of segments.

            Returns:
                New list of segments
            """
            if styles.text_opacity != 1.0:
                segments = TextOpacity.process_segments(segments, styles.text_opacity)
            if styles.tint.a:
                segments = Tint.process_segments(segments, styles.tint)
            if styles.opacity != 1.0:
                segments = _apply_opacity(segments, base_background, styles.opacity)
            return segments

        line: Iterable[Segment]
        # Draw top or bottom borders (A)
        if (border_top and y == 0) or (border_bottom and y == height - 1):
            border_color = base_background + (
                border_top_color if y == 0 else border_bottom_color
            )
            box_segments = get_box(
                border_top if y == 0 else border_bottom,
                inner,
                outer,
                from_color(color=border_color.rich_color),
            )
            line = render_row(
                box_segments[0 if y == 0 else 2],
                width,
                border_left != "",
                border_right != "",
            )

        # Draw padding (B)
        elif (pad_top and y < gutter.top) or (
            pad_bottom and y >= height - gutter.bottom
        ):
            background_style = from_color(bgcolor=background.rich_color)
            left_style = from_color(color=(background + border_left_color).rich_color)
            left = get_box(border_left, inner, outer, left_style)[1][0]
            right_style = from_color(color=(background + border_right_color).rich_color)
            right = get_box(border_right, inner, outer, right_style)[1][2]
            if border_left and border_right:
                line = [left, make_blank(width - 2, background_style), right]
            elif border_left:
                line = [left, make_blank(width - 1, background_style)]
            elif border_right:
                line = [make_blank(width - 1, background_style), right]
            else:
                line = [make_blank(width, background_style)]
        else:
            # Content with border and padding (C)
            content_y = y - gutter.top
            if content_y < content_height:
                line = render_content_line(y - gutter.top)
                line = line.adjust_cell_length(content_width)
            else:
                line = [make_blank(content_width, inner)]
            if inner:
                line = Segment.apply_style(line, inner)
            line = line_pad(line, pad_left, pad_right, inner)

            if border_left or border_right:
                # Add left / right border
                left_style = from_color(
                    (base_background + border_left_color).rich_color
                )
                left = get_box(border_left, inner, outer, left_style)[1][0]
                right_style = from_color(
                    (base_background + border_right_color).rich_color
                )
                right = get_box(border_right, inner, outer, right_style)[1][2]

                if border_left and border_right:
                    line = [left, *line, right]
                elif border_left:
                    line = [left, *line]
                else:
                    line = [*line, right]

        # Draw any outline
        if (outline_top and y == 0) or (outline_bottom and y == height - 1):
            # Top or bottom outlines
            outline_color = outline_top_color if y == 0 else outline_bottom_color
            box_segments = get_box(
                outline_top if y == 0 else outline_bottom,
                inner,
                outer,
                from_color(color=outline_color.rich_color),
            )
            line = render_row(
                box_segments[0 if y == 0 else 2],
                width,
                outline_left != "",
                outline_right != "",
            )

        elif outline_left or outline_right:
            # Lines in side outline
            left_style = from_color((base_background + outline_left_color).rich_color)
            left = get_box(outline_left, inner, outer, left_style)[1][0]
            right_style = from_color((base_background + outline_right_color).rich_color)
            right = get_box(outline_right, inner, outer, right_style)[1][2]
            line = line_trim(list(line), outline_left != "", outline_right != "")
            if outline_left and outline_right:
                line = [left, *line, right]
            elif outline_left:
                line = [left, *line]
            else:
                line = [*line, right]

        strip = Strip(post(line), width)
        return strip
