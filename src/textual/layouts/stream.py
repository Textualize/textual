from __future__ import annotations

from itertools import zip_longest
from typing import TYPE_CHECKING

from textual.geometry import NULL_OFFSET, Region, Size
from textual.layout import ArrangeResult, Layout, WidgetPlacement

if TYPE_CHECKING:
    from textual.widget import Widget


class StreamLayout(Layout):
    """A cut down version of the vertical layout.

    The stream layout is faster, but has a few limitations compared to the vertical layout.

    - All widgets are the full width (as if their widget is `1fr`).
    - All widgets have an effective height of `auto`.
    - `max-height` is supported, but only if it is a units value, all other extrema rules are ignored.
    - No absolute positioning.
    - No overlay: screen.
    - Layers are ignored.
    - Non TCSS styles are ignored.

    The primary use of `layout: stream` is for a long list of widgets in a scrolling container, such as
    what you might expect from a LLM chat-bot. The speed improvement will only be significant with a lot of
    child widgets, so stick to vertical layouts unless you see any slowdown.

    """

    name = "stream"

    def __init__(self) -> None:
        self._cached_placements: list[WidgetPlacement] | None = None
        self._cached_width = 0
        super().__init__()

    def arrange(
        self, parent: Widget, children: list[Widget], size: Size, greedy: bool = True
    ) -> ArrangeResult:
        parent.pre_layout(self)
        if not children:
            return []
        viewport = parent.app.viewport_size

        if size.width != self._cached_width:
            self._cached_placements = None
        previous_results = self._cached_placements or []

        layout_widgets = parent.screen._layout_widgets.get(parent, [])

        _Region = Region
        _WidgetPlacement = WidgetPlacement

        placements: list[WidgetPlacement] = []
        width = size.width
        first_child_styles = children[0].styles
        y = 0
        previous_margin = first_child_styles.margin.top
        null_offset = NULL_OFFSET

        pre_populate = bool(previous_results and layout_widgets)
        for widget, placement in zip_longest(children, previous_results):
            if pre_populate and placement is not None and widget is placement.widget:
                if widget in layout_widgets:
                    pre_populate = False
                else:
                    placements.append(placement)
                    y = placement.region.bottom
                    styles = widget.styles._base_styles
                    previous_margin = styles.margin.bottom
                    continue
            if widget is None:
                break

            styles = widget.styles._base_styles
            margin = styles.margin
            gutter_width, gutter_height = styles.gutter.totals
            top, right, bottom, left = margin
            y += top if top > previous_margin else previous_margin
            previous_margin = bottom
            height = (
                widget.get_content_height(size, viewport, width - gutter_width)
                + gutter_height
            )
            if (max_height := styles.max_height) is not None and max_height.is_cells:
                height = (
                    height
                    if height < (max_height_value := int(max_height.value))
                    else max_height_value
                )
            if (min_height := styles.min_height) is not None and min_height.is_cells:
                height = (
                    height
                    if height > (min_height_value := int(min_height.value))
                    else min_height_value
                )
            placements.append(
                _WidgetPlacement(
                    _Region(left, y, width - (left + right), height),
                    null_offset,
                    margin,
                    widget,
                    0,
                    False,
                    False,
                    False,
                )
            )
            y += height

        self._cached_width = size.width
        self._cached_placements = placements
        return placements

    def get_content_width(self, widget: Widget, container: Size, viewport: Size) -> int:
        """Get the optimal content width by arranging children.

        Args:
            widget: The container widget.
            container: The container size.
            viewport: The viewport size.

        Returns:
            Width of the content.
        """
        return widget.scrollable_content_region.width

    def get_content_height(
        self, widget: Widget, container: Size, viewport: Size, width: int
    ) -> int:
        """Get the content height.

        Args:
            widget: The container widget.
            container: The container size.
            viewport: The viewport.
            width: The content width.

        Returns:
            Content height (in lines).
        """
        if widget._nodes:
            arrangement = widget.arrange(Size(width, 0))
            height = arrangement.total_region.height
        else:
            height = 0
        return height
