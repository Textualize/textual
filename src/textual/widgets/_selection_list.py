"""Provides a selection list widget, allowing one or more items to be selected."""

from __future__ import annotations

from typing import Generic, TypeVar

from rich.console import RenderableType

from ._option_list import Option, OptionList

SelectionType = TypeVar("SelectionType")
"""The type for the value of a `Selection`"""


class Selection(Generic[SelectionType], Option):
    """A selection for the `SelectionList`."""

    def __init__(
        self,
        value: SelectionType,
        prompt: RenderableType,
        id: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the selection.

        Args:
            value: The value for the selection.
            prompt: The prompt for the selection.
            id: The optional ID for the selection.
            disabled: The initial enabled/disabled state. Enabled by default.
        """
        super().__init__(prompt, id, disabled)
        self._value: SelectionType = value


class SelectionList(Generic[SelectionType], OptionList):
    """A vertical option list that allows making multiple selections."""

    def __init__(
        self,
        *selections: Selection[SelectionType],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the selection list.

        Args:
            *content: The content for the selection list.
            name: The name of the selection list.
            id: The ID of the selection list in the DOM.
            classes: The CSS classes of the selection list.
            disabled: Whether the selection list is disabled or not.
        """
        super().__init__(
            *selections, name=name, id=id, classes=classes, disabled=disabled
        )
