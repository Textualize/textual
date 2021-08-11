from __future__ import annotations

from dataclasses import dataclass, field, InitVar
from logging import getLogger
from platform import mac_ver
from typing import Generic, Literal, TypeVar, TypedDict, cast

from rich.console import RenderableType
from rich.style import StyleType
from rich.panel import Panel
from rich.align import Align
import rich.repr

from ._button import ButtonRenderable
from ._scroll_view import ScrollView
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

    @container.setter
    def container(self, new: Tabs):
        if hasattr(self, "_container"):
            raise RuntimeError("Can only bind tab handle to one container.")
        self._container = new

    selected: Reactive[bool] = Reactive(False)
    current_style: Reactive[StyleMode] = Reactive("default")

    def render(self) -> RenderableType:
        return Panel(Align.center(self.label, style=self.styles[self.current_style]))

    async def on_click(self, event: events.Click) -> None:
        self._container.current = self.label

    async def on_enter(self, event: events.Enter) -> None:
        self.current_style = "selected_hover" if self.selected else "default_hover"

    async def on_leave(self, event: events.Leave) -> None:
        self.current_style = "selected" if self.selected else "default"

    async def watch_selected(self, selected: bool):
        self.current_style = "selected" if selected else "default"


class _InitTabType(str):
    """Simple sentinel for an uninitialized tab selection."""


INIT_TAB = _InitTabType()


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

    def bind(self, container: Tabs):
        self.handle.container = container

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
        initial_selection: str | None = None,
        name: str | None = None,
    ) -> None:
        if not tabs:
            raise ValueError("Tabs requires at least on Tab to function.")
        self._tabs = tabs
        self._init = initial_selection or tabs[0].name
        super().__init__(name=name)

    async def on_mount(self, event: events.Mount) -> None:
        max_column = len(self._tabs)
        grid = await self.dock_grid()
        grid.add_column("col", repeat=max_column)
        grid.add_row("bar", max_size=3)
        grid.add_row("content")
        grid.add_areas(content=f"col1-start|col{max_column}-end,content")
        for tab in self._tabs:
            tab.bind(self)
            grid.place(tab.handle, content=tab.view)
        await super().on_mount(event)
        self.current = self._init

    current: Reactive[str] = Reactive(INIT_TAB)

    async def watch_current(self, new: str) -> None:
        for tab in self._tabs:
            tab.selected = tab.name == new
