from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Iterator, Sequence, overload
from weakref import ref

import rich.repr

if TYPE_CHECKING:
    from .app import App
    from .widget import Widget


class AppChildrenView(Sequence["Widget"]):
    """Presents a view of the App's children which contains only the current screen."""

    def __init__(self, app: App) -> None:
        self._app = ref(app)

    @property
    def app(self) -> App | None:
        return self._app()

    @property
    def _updates(self) -> int:
        app = self.app
        assert app is not None
        return app.children._updates

    @property
    def _nodes(self) -> Sequence[Widget]:
        app = self.app
        if app is None:
            return []
        from .app import ScreenError

        try:
            return [app.screen]
        except ScreenError:
            return []

    def __bool__(self) -> bool:
        return bool(self._nodes)

    def __length_hint__(self) -> int:
        return 1

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._nodes

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, widget: object) -> bool:
        return widget in self._nodes

    def index(self, widget: Any, start: int = 0, stop: int = sys.maxsize) -> int:
        """Return the index of the given widget.

        Args:
            widget: The widget to find in the node list.

        Returns:
            The index of the widget in the node list.

        Raises:
            ValueError: If the widget is not in the node list.
        """
        return self._nodes.index(widget, start, stop)

    def __iter__(self) -> Iterator[Widget]:
        return iter(self._nodes)

    def __reversed__(self) -> Iterator[Widget]:
        return reversed(self._nodes)

    @overload
    def __getitem__(self, index: int) -> Widget:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[Widget]:
        ...

    def __getitem__(self, index: int | slice) -> Widget | list[Widget]:
        return list(self._nodes)[index]
