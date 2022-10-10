import rich
from rich.console import RenderableType
from rich.panel import Panel

from textual import events
from textual.layouts.grid import GridLayout
from textual.reactive import Reactive
from textual.views import DockView
from textual.widget import Widget
from textual.widgets import ScrollView


class Tab(Widget):
    hover = Reactive(False)
    selected = Reactive(False)

    def __init__(self, content: RenderableType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = content

    @property
    def container(self) -> "TabBar":
        if not hasattr(self, "_container"):
            raise RuntimeError("Tab handle must be bound to container before use.")
        return self._container

    def bind(self, container: "TabBar", idx: int):
        if hasattr(self, "_container"):
            raise RuntimeError("Can only bind tab handle to one container.")
        self._container = container
        self._idx = idx

    @property
    def color(self) -> str:
        if self.hover and self.selected:
            return "on orange3"
        if self.hover:
            return "on red"
        elif self.selected:
            return "on green"
        else:
            return ""

    def render(self) -> Panel:
        return Panel(self.name, style=(self.color))

    async def on_enter(self) -> None:
        self.hover = True

    async def on_leave(self) -> None:
        self.hover = False

    async def on_click(self, *args, **kwargs) -> None:
        self.container.current = self._idx


@rich.repr.auto
class TabBar(DockView):
    def __init__(
        self,
        tabs: list[Tab],
        main_view: ScrollView,
        initial_selection: int | None = None,
        name: str | None = None,
    ) -> None:
        if not tabs:
            raise ValueError("TabBar requires at least on Tab to function.")
        self._tabs = tabs
        self._init = initial_selection or 0
        self.view = main_view
        super().__init__(name=name)

    def init_grid(self, grid: GridLayout) -> None:
        max_column = len(self._tabs)
        grid.add_column("col", repeat=max_column)
        grid.add_row("bar", size=3)

    async def on_mount(self, event: events.Mount) -> None:
        grid = await self.dock_grid()
        self.init_grid(grid)

        for i, tab in enumerate(self._tabs):
            tab.bind(self, i)
            grid.place(tab)

        await super().on_mount(event)
        self.current = self._init
        await self.view.update(tab.content)

    current: Reactive[int] = Reactive(0)

    async def watch_current(self, old: int, new: int) -> None:
        self._tabs[old].selected = False
        tab = self._tabs[new]
        tab.selected = True
        await self.view.update(tab.content, home=False)
