"""Provides a widget for switching between the display of its immediate children."""

from __future__ import annotations

from typing import Optional

from ..containers import Container
from ..css.query import NoMatches
from ..events import Mount
from ..reactive import reactive
from ..widget import Widget


class ContentSwitcher(Container):
    """A widget for switching between different children.

    Note:
        All child widgets that are to be switched between need a unique ID.
        Children that have no ID will be hidden and ignored.
    """

    DEFAULT_CSS = """
    ContentSwitcher {
        height: auto;
    }

    """

    current: reactive[str | None] = reactive[Optional[str]](None, init=False)
    """The ID of the currently-displayed widget.

    If set to `None` then no widget is visible.

    Note:
        If set to an unknown ID, this will result in
        [`NoMatches`][textual.css.query.NoMatches] being raised.
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        initial: str | None = None,
    ) -> None:
        """Initialise the content switching widget.

        Args:
            *children: The widgets to switch between.
            name: The name of the content switcher.
            id: The ID of the content switcher in the DOM.
            classes: The CSS classes of the content switcher.
            disabled: Whether the content switcher is disabled or not.
            initial: The ID of the initial widget to show, ``None`` or empty string for the first tab.

        Note:
            If `initial` is not supplied no children will be shown to start with.
        """
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._initial = initial

    def _on_mount(self, _: Mount) -> None:
        """Perform the initial setup of the widget once the DOM is ready."""
        initial = self._initial
        with self.app.batch_update():
            for child in self.children:
                child.display = bool(initial) and child.id == initial
        self._reactive_current = initial

    @property
    def visible_content(self) -> Widget | None:
        """A reference to the currently-visible widget.

        `None` if nothing is visible.
        """
        return self.get_child_by_id(self.current) if self.current is not None else None

    def watch_current(self, old: str | None, new: str | None) -> None:
        """React to the current visible child choice being changed.

        Args:
            old: The old widget ID (or `None` if there was no widget).
            new: The new widget ID (or `None` if nothing should be shown).
        """
        with self.app.batch_update():
            if old:
                try:
                    self.get_child_by_id(old).display = False
                except NoMatches:
                    pass
            if new:
                self.get_child_by_id(new).display = True
