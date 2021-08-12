from __future__ import annotations

from dataclasses import dataclass, field, InitVar
from logging import getLogger
from typing import Generic, Literal, TypeVar, TypedDict, cast

from rich.console import RenderableType
from rich.style import StyleType
from rich.panel import Panel
from rich.align import Align
import rich.repr

from .. import events, views
from ..widget import Reactive, Widget
from ..view import View

log = getLogger("rich")

ViewType = TypeVar("ViewType", bound=View)


class HandleStyle(TypedDict):
    default: StyleType
    default_hover: StyleType
    selected: StyleType
    selected_hover: StyleType


StyleMode = Literal["default", "default_hover", "selected", "selected_hover"]


class TabHandle(Widget):
    def __init__(
        self,
        label: str,
        name: str | None = None,
        styles: HandleStyle | None = None,
    ) -> None:
        self.label = label
        self.styles: HandleStyle = styles or cast(
            HandleStyle,
            {
                "default": "default",
                "default_hover": "reverse",
                "selected": "bold",
                "selected_hover": "bold reverse",
            },
        )
        super().__init__(name=name)

    @property
    def container(self) -> Tabs:
        if not hasattr(self, "_container"):
            raise RuntimeError("Tab handle must be bound to container before use.")
        return self._container

    def bind(self, container: Tabs, idx: int):
        if hasattr(self, "_container"):
            raise RuntimeError("Can only bind tab handle to one container.")
        self._container = container
        self._idx = idx

    selected: Reactive[bool] = Reactive(False)
    hover: Reactive[bool] = Reactive(False)

    def render(self) -> RenderableType:
        return Panel(Align.center(self.label, style=self.styles[self._current_style]))

    @property
    def _current_style(self) -> StyleMode:
        return cast(
            StyleMode, ("default", "selected")[self.selected] + "_hover" * self.hover
        )

    async def on_click(self, event: events.Click) -> None:
        self.container.current = self._idx

    async def on_enter(self, event: events.Enter) -> None:
        self.hover = True

    async def on_leave(self, event: events.Leave) -> None:
        self.hover = False


@dataclass
class Tab(Generic[ViewType]):
    name: str
    view_type: InitVar[type[ViewType]] = views.DockView
    handle_styles: InitVar[HandleStyle | None] = None
    view: ViewType = field(init=False)
    handle: TabHandle = field(init=False)
    _selected: bool = field(init=False, default=False)

    def __post_init__(
        self, view_type: type[ViewType], handle_styles: HandleStyle | None
    ):
        if not self.name:
            raise ValueError("A Tabs name must be at least one character long.")
        self.view = view_type()
        self.handle = TabHandle(self.name, styles=handle_styles)

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, new: bool):
        self.view.visible = new
        self.handle.selected = new


@rich.repr.auto
class Tabs(views.DockView):
    def __init__(
        self,
        tabs: list[Tab],
        initial_selection: int | None = None,
        name: str | None = None,
    ) -> None:
        if not tabs:
            raise ValueError("Tabs requires at least on Tab to function.")
        self._tabs = tabs
        self._init = initial_selection or 0
        super().__init__(name=name)

    async def on_mount(self, event: events.Mount) -> None:
        max_column = len(self._tabs)
        grid = await self.dock_grid()
        grid.add_column("col", repeat=max_column)
        grid.add_row("bar", size=3)
        grid.add_row("content")
        grid.add_areas(content=f"col1-start|col{max_column}-end,content")
        for i, tab in enumerate(self._tabs):
            tab.handle.bind(self, i)
            grid.place(tab.handle, content=tab.view)
        await super().on_mount(event)
        self.current = self._init

    current: Reactive[int] = Reactive(0)

    async def watch_current(self, old: int, new: int) -> None:
        self._tabs[old].selected = False
        self._tabs[new].selected = True
