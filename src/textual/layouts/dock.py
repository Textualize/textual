from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from rich._ratio import ratio_resolve

from ..widget import WidgetID
from ..geometry import Region
from ..layout import Layout, LayoutMap, MapRegion

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


if TYPE_CHECKING:
    from ..widget import WidgetBase


DockEdge = Literal["top", "right", "bottom", "left"]


@dataclass
class DockOptions:
    size: int | None = None
    fraction: int = 1
    minimum_size: int = 1

    @property
    def ratio(self) -> int:
        return self.fraction


@dataclass
class Dock:
    edge: DockEdge
    widgets: Sequence[WidgetID]
    z: int = 0


class DockLayout(Layout):
    def __init__(self) -> None:
        self.docks: list[Dock] = []
        super().__init__()

    def __call__(
        self, widgets: dict[WidgetID, WidgetBase], width: int, height: int
    ) -> LayoutMap:
        render_width = width
        render_height = height
        map: dict[WidgetID, MapRegion] = {}
        region = Region(0, 0, width, height)

        layers: dict[int, Region] = defaultdict(lambda: Region(0, 0, width, height))

        for index, dock in enumerate(self.docks):
            dock_widgets = [widgets[widget_id] for widget_id in dock.widgets]
            dock_options = [
                DockOptions(
                    widget.dock_size, widget.dock_fraction, widget.dock_minimum_size
                )
                for widget in dock_widgets
            ]

            region = layers[dock.z]
            if not region:
                continue

            order = (dock.z, index)
            x, y, width, height = region

            if dock.edge == "top":
                sizes = ratio_resolve(height, dock_options)
                render_y = y
                remaining = region.height
                total = 0
                for widget_id, size in zip(dock.widgets, sizes):
                    widget = widgets[widget_id]
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    render_region = (
                        Region(x, render_y, width, size) + widget.dock_offset
                    )
                    map[widget.id] = MapRegion(render_region, order)
                    render_y += size
                    remaining = max(0, remaining - size)
                region = Region(x, y + total, width, height - total)

            elif dock.edge == "bottom":
                sizes = ratio_resolve(height, dock_options)
                render_y = y + height
                remaining = region.height
                total = 0
                for widget_id, size in zip(dock.widgets, sizes):
                    widget = widgets[widget_id]
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    render_region = (
                        Region(x, render_y - size, width, size) + widget.dock_offset
                    )
                    map[widget.id] = MapRegion(render_region, order)
                    render_y -= size
                    remaining = max(0, remaining - size)
                region = Region(x, y, width, height - total)

            elif dock.edge == "left":
                sizes = ratio_resolve(width, dock_options)
                render_x = x
                remaining = region.width
                total = 0
                for widget_id, size in zip(dock.widgets, sizes):
                    widget = widgets[widget_id]
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size

                    render_region = (
                        Region(render_x, y, size, height) + widget.dock_offset
                    )
                    map[widget.id] = MapRegion(render_region, order)
                    render_x += size
                    remaining = max(0, remaining - size)
                region = Region(x + total, y, width - total, height)

            elif dock.edge == "right":
                sizes = ratio_resolve(height, dock_options)
                render_x = x + width
                remaining = region.width
                total = 0
                for widget_id, size in zip(dock.widgets, sizes):
                    widget = widgets[widget_id]
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    render_region = (
                        Region(render_x - size, y, size, height) + widget.dock_offset
                    )
                    map[widget.id] = MapRegion(render_region, order)
                    render_x -= size
                    remaining = max(0, remaining - size)
                region = Region(x, y, width - total, height)

            layers[dock.z] = region

        return LayoutMap(map, render_width, render_height)


if __name__ == "__main__":

    from ..widgets.placeholder import Placeholder

    widget1 = Placeholder()
    widget1.dock_size = 3

    widget2 = Placeholder()
    widget3 = Placeholder()

    widget3.style = "on dark_blue"
    widget3.dock_size = 40
    # widget3.dock_offset = Point(-20, +1)

    widget4 = Placeholder()
    widget4.dock_size = 1

    widget5 = Placeholder()
    widget5.dock_fraction = 1

    widget6 = Placeholder()
    widget6.dock_fraction = 1

    widgets: dict[WidgetID, WidgetBase] = {
        widget1.id: widget1,
        widget2.id: widget2,
        widget3.id: widget3,
        widget4.id: widget4,
        widget5.id: widget5,
        widget6.id: widget6,
    }

    layout = DockLayout()
    layout.docks = [
        Dock(
            "top",
            [
                widget1.id,
            ],
        ),
        Dock(
            "left",
            [
                widget3.id,
            ],
            z=1,
        ),
        Dock(
            "bottom",
            [
                widget4.id,
            ],
        ),
        Dock(
            "left",
            [
                widget5.id,
                widget6.id,
            ],
        ),
    ]

    # fmt: on
    from rich import print
    from rich.console import Console

    console = Console()

    width, height = console.size
    map = layout(widgets, width, height)

    print(map.render(widgets, console))
    # print(render(map, widgets, console, width, height))
    # for widget, (region, lines) in layout.map.items():
    #     print(repr(widget), region)

    # from rich import print

    # print(layout)
