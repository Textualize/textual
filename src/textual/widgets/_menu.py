"""Provides the core of a classic vertical bounce-bar menu."""

from __future__ import annotations

from typing import Generic, TypeVar

from ..scroll_view import ScrollView

MenuDataType = TypeVar("MenuDataType")
"""The type of the data for a given instance of a [Menu][textual.widgets.Menu]."""


class MenuItem(Generic[MenuDataType]):
    """Class that holds the details of an individual menu item."""


class Menu(Generic[MenuDataType], ScrollView, can_focus=True):
    """A vertical bounce-bar menu."""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the menu.

        Args:
            name: The name of the Tree.
            id: The ID of the tree in the DOM.
            classes: The CSS classes of the tree.
            disabled: Whether the tree is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._items: list[MenuItem[MenuDataType]] = []
