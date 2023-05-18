"""Provides a selection list widget, allowing one or more items to be selected."""

from __future__ import annotations

from typing import ClassVar, Generic, TypeVar

from rich.console import RenderableType
from rich.style import Style
from rich.text import Text, TextType

from ..binding import Binding
from ._option_list import Option, OptionList
from ._toggle_button import ToggleButton

SelectionType = TypeVar("SelectionType")
"""The type for the value of a `Selection`"""


class Selection(Generic[SelectionType], Option):
    """A selection for the `SelectionList`."""

    def __init__(
        self,
        parent: SelectionList,
        value: SelectionType,
        prompt: TextType,
        id: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the selection.

        Args:
            value: The value for the selection.
            prompt: The prompt for the selection.
            selected: Is this particular selection selected?
            id: The optional ID for the selection.
            disabled: The initial enabled/disabled state. Enabled by default.
        """
        self._prompt = prompt
        self._parent = parent
        super().__init__(prompt, id, disabled)
        self._value: SelectionType = value

    @property
    def value(self) -> SelectionType:
        """The value for this selection."""
        return self._value

    @property
    def prompt(self) -> RenderableType:
        return self._parent._make_label(self)

    @property
    def selected(self) -> bool:
        return self._value in self._parent._selected


class SelectionList(Generic[SelectionType], OptionList):
    """A vertical option list that allows making multiple selections."""

    BINDINGS = [Binding("space, enter", "toggle"), Binding("x", "redraw")]

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "selection-list--button",
        "selection-list--button-selected",
    }

    DEFAULT_CSS = """
    /* Base button colours (including in dark mode). */

    SelectionList > .selection-list--button {
        color: $background;
        text-style: bold;
        background: $foreground 15%;
    }

    SelectionList:focus > .selection-list--button {
        background: $foreground 25%;
        background: red;
        color: red;
    }

    SelectionList > .selection-list--button-selected {
        color: $success;
        text-style: bold;
    }

    SelectionList:focus > .selection-list--button-selected {
        background: $foreground 25%;
    }
    """

    def __init__(
        self,
        *selections: tuple[SelectionType, TextType]
        | tuple[SelectionType, TextType, bool],
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
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._selected: dict[SelectionType, None] = {}
        self._selections = selections

    def _on_mount(self):
        self.add_options(
            [self._make_selection(selection) for selection in self._selections]
        )
        if self.option_count:
            self.highlighted = 0

    def _make_label(self, selection: Selection) -> Text:
        # Grab the button style.
        button_style = self.get_component_rich_style(
            f"selection-list--button{'-selected' if selection.selected else ''}"
        )

        # If the button is off, we're going to do a bit of a switcharound to
        # make it look like it's a "cutout".
        if not selection.selected:
            button_style += Style.from_color(
                self.background_colors[1].rich_color, button_style.bgcolor
            )

        # Building the style for the side characters. Note that this is
        # sensitive to the type of character used, so pay attention to
        # BUTTON_LEFT and BUTTON_RIGHT.
        side_style = Style.from_color(
            button_style.bgcolor, self.background_colors[1].rich_color
        )

        return Text.assemble(
            (ToggleButton.BUTTON_LEFT, side_style),
            (ToggleButton.BUTTON_INNER, button_style),
            (ToggleButton.BUTTON_RIGHT, side_style),
            " ",
            selection._prompt,
        )

    def _make_selection(
        self,
        selection: tuple[SelectionType, TextType]
        | tuple[SelectionType, TextType, bool],
    ) -> Selection[SelectionType]:
        """Turn incoming selection data into a `Selection` instance.

        Args:
            selection: The selection data.

        Returns:
            An instance of a `Selection`.
        """
        if len(selection) == 3:
            value, label, selected = selection
        elif len(selection) == 2:
            value, label, selected = (*selection, False)
        else:
            # TODO: Proper error.
            raise TypeError("Wrong number of values for a selection.")
        if selected:
            self._selected[value] = None
        return Selection(self, value, label)

    def action_toggle(self) -> None:
        if self.highlighted is not None:
            option = self.get_option_at_index(self.highlighted)
            assert isinstance(option, Selection)
            if option.selected:
                del self._selected[option._value]
            else:
                self._selected[option._value] = None
            self._refresh_content_tracking(force=True)
            self.refresh()
