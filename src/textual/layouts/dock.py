from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Mapping, Sequence

from rich._ratio import ratio_resolve

from ..widget import WidgetID
from ..geometry import Region, Point
from ..layout import Layout, MapRegion
from .._types import Lines

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


if TYPE_CHECKING:
    from ..widget import Widget

log = logging.getLogger("rich")


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
    widgets: Sequence[Widget]
    z: int = 0


class DockLayout(Layout):
    def __init__(self, docks: list[Dock] = None) -> None:
        self.docks: list[Dock] = docks or []
        super().__init__()

    def reflow(self, width: int, height: int, offset: Point = Point(0, 0)) -> None:
        self.reset()
        self.width = width
        self.height = height
        map: dict[Widget, MapRegion] = {}

        layers: dict[int, Region] = defaultdict(
            lambda: Region(0, 0, self.width, self.height)
        )

        def add_widget(widget: Widget, region: Region, order: tuple[int, int]):
            region = region + offset
            if hasattr(widget, "layout"):
                widget.layout.reflow(
                    region.width, region.height, offset=region.origin + offset
                )
                map.update(widget.layout.map)
            else:
                map[widget] = MapRegion(region + widget.layout_offset, order)

        for index, dock in enumerate(self.docks):
            dock_options = [
                DockOptions(
                    widget.layout_size,
                    widget.layout_fraction,
                    widget.layout_minimim_size,
                )
                for widget in dock.widgets
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
                for widget, size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    render_region = (
                        Region(x, render_y, width, size) + widget.layout_offset
                    )
                    add_widget(widget, render_region, order)
                    render_y += size
                    remaining = max(0, remaining - size)
                region = Region(x, y + total, width, height - total)

            elif dock.edge == "bottom":
                sizes = ratio_resolve(height, dock_options)
                render_y = y + height
                remaining = region.height
                total = 0
                for widget, size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    render_region = (
                        Region(x, render_y - size, width, size) + widget.layout_offset
                    )
                    add_widget(widget, render_region, order)
                    render_y -= size
                    remaining = max(0, remaining - size)
                region = Region(x, y, width, height - total)

            elif dock.edge == "left":
                sizes = ratio_resolve(width, dock_options)
                render_x = x
                remaining = region.width
                total = 0
                for widget, size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    render_region = (
                        Region(render_x, y, size, height) + widget.layout_offset
                    )
                    add_widget(widget, render_region, order)
                    render_x += size
                    remaining = max(0, remaining - size)
                region = Region(x + total, y, width - total, height)

            elif dock.edge == "right":
                sizes = ratio_resolve(width, dock_options)
                render_x = x + width
                remaining = region.width
                total = 0
                for widget, size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    render_region = (
                        Region(render_x - size, y, size, height) + widget.layout_offset
                    )
                    add_widget(widget, render_region, order)
                    render_x -= size
                    remaining = max(0, remaining - size)
                region = Region(x, y, width - total, height)

            layers[dock.z] = region

        new_renders: dict[Widget, tuple[Region, Lines]] = {}
        for widget, (region, order) in map.items():
            if widget in self.renders and self.renders[widget][0].size == region.size:
                new_renders[widget] = (region, self.renders[widget][1])

        self.renders = new_renders
        log.debug("DOCK")
        self._layout_map = map


if __name__ == "__main__":

    from ..widgets.placeholder import Placeholder

    import os.path

    readme_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../richreadme.md"
    )
    from rich.markdown import Markdown
    from ..widget import StaticWidget

    with open(readme_path) as f:
        markdown = Markdown(f.read())

    widget1 = StaticWidget(markdown)
    widget1.layout_size = 3

    widget2 = StaticWidget(markdown)
    widget3 = Placeholder()

    widget3.style = "on dark_blue"
    widget3.layout_size = 40
    widget3.layout_offset_x = +10
    widget3.layout_offset_y = +5
    # widget3.dock_offset = Point(-20, +1)

    widget4 = Placeholder()
    widget4.layout_size = 1

    widget5 = StaticWidget(markdown)
    widget5.layout_fraction = 1

    widget6 = StaticWidget(markdown)
    widget6.layout_fraction = 1

    widgets: dict[WidgetID, Widget] = {
        widget1.id: widget1,
        widget2.id: widget2,
        widget3.id: widget3,
        widget4.id: widget4,
        widget5.id: widget5,
        widget6.id: widget6,
    }

    docks = [
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
    layout = DockLayout(docks)

    # fmt: on
    from rich import print
    from rich.console import Console
    from rich.segment import Segments, SegmentLines

    console = Console()

    width, height = console.size

    layout.reflow(widgets, width, height)

    print(layout.render(widgets, console))

    widget3.style = "on red"
    # print(
    #     layout.render(
    #         widgets,
    #         console,
    #     )
    # )
    console.clear()

    print(layout.update_widget(widgets, console, widget3))
