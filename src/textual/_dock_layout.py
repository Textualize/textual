from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

from rich._ratio import ratio_resolve
from rich.segment import Segment

from .geometry import Point, Region
from .widget import WidgetBase
from .layout import LayoutBase, RegionRender


# class Edge(Protocol):
#     """Any object that defines an edge (such as Layout)."""

#     size: Optional[int] = None
#     ratio: int = 1
#     minimum_size: int = 1


class DockSide(Enum):
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4


@dataclass
class Dock:
    side: DockSide
    widgets: list[DockWidget]
    z: int = 0


@dataclass
class DockWidget:
    widget: WidgetBase
    size: int | None = None
    fraction: int = 1
    minimum_size: int = 1

    @property
    def ratio(self) -> int:
        return self.fraction


class DockLayout(LayoutBase):
    def __init__(self, docks: list[Dock]) -> None:
        self.docks = docks
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

            if dock.side == DockSide.TOP:
                sizes = ratio_resolve(height, dock.widgets)
                render_y = y
                remaining = region.height
                total = 0
                for dock_widget, size in zip(dock.widgets, sizes):
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    widget = dock_widget.widget
                    lines = render(widget, width, size)
                    render_region = Region(x, render_y, width, size) + widget.offset
                    map[widget] = RegionRender(render_region, lines, order)
                    render_y += size
                    remaining = max(0, remaining - size)
                region = Region(x, y + total, width, height - total)

            elif dock.side == DockSide.BOTTOM:
                sizes = ratio_resolve(height, dock.widgets)
                render_y = y + height
                remaining = region.height
                total = 0
                for dock_widget, size in zip(dock.widgets, sizes):
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    widget = dock_widget.widget
                    lines = render(widget, width, size)
                    render_region = (
                        Region(x, render_y - size, width, size) + widget.offset
                    )
                    map[widget] = RegionRender(render_region, lines, order)
                    render_y -= size
                    remaining = max(0, remaining - size)
                region = Region(x, y, width, height - total)

            elif dock.side == DockSide.LEFT:
                sizes = ratio_resolve(width, dock.widgets)
                render_x = x
                remaining = region.width
                total = 0
                for dock_widget, size in zip(dock.widgets, sizes):
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    widget = dock_widget.widget
                    lines = render(widget, size, height)
                    render_region = Region(render_x, y, size, height) + widget.offset
                    map[widget] = RegionRender(render_region, lines, order)
                    render_x += size
                    remaining = max(0, remaining - size)
                region = Region(x + total, y, width - total, height)

            elif dock.side == DockSide.RIGHT:
                sizes = ratio_resolve(height, dock.widgets)
                render_x = x + width
                remaining = region.width
                total = 0
                for dock_widget, size in zip(dock.widgets, sizes):
                    size = min(remaining, size)
                    if not size:
                        break
                    total += size
                    widget = dock_widget.widget
                    lines = render(widget, size, height)
                    render_region = (
                        Region(render_x - size, y, size, height) + widget.offset
                    )
                    map[widget] = RegionRender(render_region, lines, order)
                    render_x -= size
                    remaining = max(0, remaining - size)
                region = Region(x, y, width - total, height)

            layers[dock.z] = region

        # print(layers)
        # print(map)


if __name__ == "__main__":

    from .widgets.placeholder import Placeholder

    # fmt: off
    widget1 = Placeholder()
    widget2 = Placeholder()
    widget3 = Placeholder()
    widget3.style = "on dark_blue"
    widget3.offset = Point(150, 10)
    widget4 = Placeholder()
    widget5 = Placeholder()
    widget6 = Placeholder()
    layout = DockLayout(
        [
            Dock(
                DockSide.TOP,
                [
                    DockWidget(widget1, size=3),                    
                    
                ]
            ),
            Dock(
                DockSide.LEFT,
                [                    
                    DockWidget(widget3, size=30),                                        
                ],z=1
            ),
            Dock(
                DockSide.BOTTOM,
                [
                    DockWidget(widget4, size=5),  
              
                ]
            ),
            Dock(
                DockSide.LEFT,
                [
                    DockWidget(widget5, fraction=1),  
                    DockWidget(widget6, fraction=1),                                        
                ]
            ),
        ]
    )
    # fmt: on
    from rich import print
    from rich.console import Console

    console = Console()

    layout.reflow(console, console.width, console.height)

    # for widget, (region, lines) in layout.map.items():
    #     print(repr(widget), region)

    from rich import print

    print(layout)
