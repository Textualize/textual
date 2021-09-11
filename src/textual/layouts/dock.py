from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, TYPE_CHECKING, Sequence

from rich.console import Console

from .._layout_resolve import layout_resolve
from ..geometry import Offset, Region, Size
from ..layout import Layout, WidgetPlacement
from ..layout_map import LayoutMap

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


if TYPE_CHECKING:
    from ..widget import Widget


DockEdge = Literal["top", "right", "bottom", "left"]


@dataclass
class DockOptions:
    size: int | None = None
    fraction: int = 1
    min_size: int = 1


@dataclass
class Dock:
    edge: DockEdge
    widgets: Sequence[Widget]
    z: int = 0


class DockLayout(Layout):
    def __init__(self, docks: list[Dock] = None) -> None:
        self.docks: list[Dock] = docks or []
        super().__init__()

    def get_widgets(self) -> Iterable[Widget]:
        for dock in self.docks:
            yield from dock.widgets

    def arrange(self, size: Size, scroll: Offset) -> Iterable[WidgetPlacement]:

        map: LayoutMap = LayoutMap(size)
        width, height = size
        layout_region = Region(0, 0, width, height)
        layers: dict[int, Region] = defaultdict(lambda: layout_region)

        for index, dock in enumerate(self.docks):
            dock_options = [
                DockOptions(
                    widget.layout_size, widget.layout_fraction, widget.layout_min_size
                )
                for widget in dock.widgets
            ]
            region = layers[dock.z]
            if not region:
                # No space left
                continue

            order = (dock.z, index)
            x, y, width, height = region

            if dock.edge == "top":
                sizes = layout_resolve(height, dock_options)
                render_y = y
                remaining = region.height
                total = 0
                for widget, layout_size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    layout_size = min(remaining, layout_size)
                    if not layout_size:
                        break
                    total += layout_size
                    yield WidgetPlacement(
                        Region(x, render_y, width, layout_size), widget, order
                    )
                    render_y += layout_size
                    remaining = max(0, remaining - layout_size)
                region = Region(x, y + total, width, height - total)

            elif dock.edge == "bottom":
                sizes = layout_resolve(height, dock_options)
                render_y = y + height
                remaining = region.height
                total = 0
                for widget, layout_size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    layout_size = min(remaining, layout_size)
                    if not layout_size:
                        break
                    total += layout_size
                    yield WidgetPlacement(
                        Region(x, render_y - layout_size, width, layout_size),
                        widget,
                        order,
                    )
                    render_y -= layout_size
                    remaining = max(0, remaining - layout_size)
                region = Region(x, y, width, height - total)

            elif dock.edge == "left":
                sizes = layout_resolve(width, dock_options)
                render_x = x
                remaining = region.width
                total = 0
                for widget, layout_size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    layout_size = min(remaining, layout_size)
                    if not layout_size:
                        break
                    total += layout_size
                    yield WidgetPlacement(
                        Region(render_x, y, layout_size, height),
                        widget,
                        order,
                    )
                    render_x += layout_size
                    remaining = max(0, remaining - layout_size)
                region = Region(x + total, y, width - total, height)

            elif dock.edge == "right":
                sizes = layout_resolve(width, dock_options)
                render_x = x + width
                remaining = region.width
                total = 0
                for widget, layout_size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    layout_size = min(remaining, layout_size)
                    if not layout_size:
                        break
                    total += layout_size
                    yield WidgetPlacement(
                        Region(render_x - layout_size, y, layout_size, height),
                        widget,
                        order,
                    )
                    render_x -= layout_size
                    remaining = max(0, remaining - layout_size)
                region = Region(x, y, width - total, height)

            layers[dock.z] = region

        return map
