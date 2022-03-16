from __future__ import annotations

from typing import Iterable

from .geometry import Size, Offset, Region
from .layout import WidgetPlacement
from .widget import Widget


def arrange(
    widget: Widget, size: Size, scroll: Offset
) -> tuple[list[WidgetPlacement], set[Widget]]:

    assert widget.layout is not None

    placements, widgets = widget.layout.arrange(
        widget,
        size - (widget.show_vertical_scrollbar, widget.show_horizontal_scrollbar),
        scroll,
    )

    return placements, widgets
