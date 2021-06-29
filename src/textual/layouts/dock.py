from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
import sys
from typing import Sequence, TYPE_CHECKING

from rich._ratio import ratio_resolve
from rich.segment import Segment


from ..geometry import Point, Region
from ..layout import LayoutBase, RegionRender

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
    widgets: Sequence[WidgetBase]
    z: int = 0

    @property
    def options(self) -> list[DockOptions]:
        def make_options(widget: WidgetBase) -> DockOptions:
            return DockOptions(
                widget.dock_size, widget.dock_fraction, widget.dock_minimum_size
            )

        return [make_options(widget) for widget in self.widgets]


class DockLayout(LayoutBase):
    def __init__(self) -> None:
        self.docks: list[Dock] = []
        super().__init__()

    def reflow(self, console, width: int, height: int) -> None:
        self.map.clear()
        map = self.map
        options = console.options

        def render(widget: WidgetBase, width: int, height: int) -> list[list[Segment]]:
            lines = console.render_lines(
                widget, options.update_dimensions(width, height)
            )
            return lines

        region = Region(0, 0, width, height)

        layers: dict[int, Region] = defaultdict(lambda: Region(0, 0, width, height))

        for index, dock in enumerate(self.docks):
            region = layers[dock.z]

            order = (dock.z, index)

            if not region:
                continue
            x, y, width, height = region

            if dock.edge == "top":
                sizes = ratio_resolve(height, dock.options)
                render_y = y
                remaining = region.height
                total = 0
                for widget, size in zip(dock.widgets, sizes):
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    lines = render(widget, width, size)
                    render_region = (
                        Region(x, render_y, width, size) + widget.dock_offset
                    )
                    map[widget] = RegionRender(render_region, lines, order)
                    render_y += size
                    remaining = max(0, remaining - size)
                region = Region(x, y + total, width, height - total)

            elif dock.edge == "bottom":
                sizes = ratio_resolve(height, dock.options)
                render_y = y + height
                remaining = region.height
                total = 0
                for widget, size in zip(dock.widgets, sizes):
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    lines = render(widget, width, size)
                    render_region = (
                        Region(x, render_y - size, width, size) + widget.dock_offset
                    )
                    map[widget] = RegionRender(render_region, lines, order)
                    render_y -= size
                    remaining = max(0, remaining - size)
                region = Region(x, y, width, height - total)

            elif dock.edge == "left":
                sizes = ratio_resolve(width, dock.options)
                render_x = x
                remaining = region.width
                total = 0
                for widget, size in zip(dock.widgets, sizes):
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    lines = render(widget, size, height)
                    render_region = (
                        Region(render_x, y, size, height) + widget.dock_offset
                    )
                    map[widget] = RegionRender(render_region, lines, order)
                    render_x += size
                    remaining = max(0, remaining - size)
                region = Region(x + total, y, width - total, height)

            elif dock.edge == "right":
                sizes = ratio_resolve(height, dock.options)
                render_x = x + width
                remaining = region.width
                total = 0
                for widget, size in zip(dock.widgets, sizes):
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    lines = render(widget, size, height)
                    render_region = (
                        Region(render_x - size, y, size, height) + widget.dock_offset
                    )
                    map[widget] = RegionRender(render_region, lines, order)
                    render_x -= size
                    remaining = max(0, remaining - size)
                region = Region(x, y, width - total, height)

            layers[dock.z] = region

        # print(layers)
        # print(map)


if __name__ == "__main__":

    from ..widgets.placeholder import Placeholder

    widget1 = Placeholder()
    widget1.dock_size = 3

    widget2 = Placeholder()
    widget3 = Placeholder()

    widget3.style = "on dark_blue"
    widget3.dock_size = 60
    widget3.dock_offset = Point(-20, +1)

    widget4 = Placeholder()
    widget4.dock_size = 1

    widget5 = Placeholder()
    widget5.dock_fraction = 1

    widget6 = Placeholder()
    widget6.dock_fraction = 1

    layout = DockLayout()
    layout.docks = [
        Dock(
            "top",
            [
                widget1,
            ],
        ),
        Dock(
            "left",
            [
                widget3,
            ],
            z=1,
        ),
        Dock(
            "bottom",
            [
                widget4,
            ],
        ),
        Dock(
            "left",
            [
                widget5,
                widget6,
            ],
        ),
    ]

    # fmt: on
    from rich import print
    from rich.console import Console

    console = Console()

    layout.reflow(console, console.width, console.height)

    print(layout.map)

    # for widget, (region, lines) in layout.map.items():
    #     print(repr(widget), region)

    from rich import print

    print(layout)
