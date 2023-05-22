"""Provides a selection list widget, allowing one or more items to be selected."""

from __future__ import annotations

from typing import ClassVar, Generic, TypeVar, cast

from rich.repr import Result
from rich.segment import Segment
from rich.style import Style
from rich.text import TextType

from ..binding import Binding
from ..messages import Message
from ..strip import Strip
from ._option_list import Option, OptionList
from ._toggle_button import ToggleButton

SelectionType = TypeVar("SelectionType")
"""The type for the value of a `Selection`"""
MessageSelectionType = TypeVar("MessageSelectionType")
"""The type for the value of a `SelectionList` message"""


class Selection(Generic[SelectionType], Option):
    """A selection for the `SelectionList`."""

    def __init__(
        self,
        prompt: TextType,
        value: SelectionType,
        id: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the selection.

        Args:
            prompt: The prompt for the selection.
            value: The value for the selection.
            selected: Is this particular selection selected?
            id: The optional ID for the selection.
            disabled: The initial enabled/disabled state. Enabled by default.
        """
        super().__init__(prompt, id, disabled)
        self._value: SelectionType = value

    @property
    def value(self) -> SelectionType:
        """The value for this selection."""
        return self._value


class SelectionList(Generic[SelectionType], OptionList):
    """A vertical selection list that allows making multiple selections."""

    BINDINGS = [Binding("space, enter", "toggle")]

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "selection-list--button",
        "selection-list--button-selected",
        "selection-list--button-highlighted",
        "selection-list--button-selected-highlighted",
    }

    DEFAULT_CSS = """
    SelectionList > .selection-list--button {
        text-style: bold;
        background: $foreground 15%;
    }

    SelectionList:focus > .selection-list--button {
        text-style: bold;
        background: $foreground 25%;
    }

    SelectionList > .selection-list--button-highlighted {
        text-style: bold;
        background: $foreground 15%;
    }

    SelectionList:focus > .selection-list--button-highlighted {
        text-style: bold;
        background: $foreground 25%;
    }

    SelectionList > .selection-list--button-selected {
        text-style: bold;
        background: $foreground 15%;
    }

    SelectionList:focus > .selection-list--button-selected {
        text-style: bold;
        color: $success;
        background: $foreground 25%;
    }

    SelectionList > .selection-list--button-selected-highlighted {
        text-style: bold;
        color: $success;
        background: $foreground 15%;
    }

    SelectionList:focus > .selection-list--button-selected-highlighted {
        text-style: bold;
        color: $success;
        background: $foreground 25%;
    }
    """

    class SelectionMessage(Generic[MessageSelectionType], Message):
        """Base class for all selection messages."""

        def __init__(self, selection_list: SelectionList, index: int) -> None:
            """Initialise the selection message.

            Args:
                selection_list: The selection list that owns the selection.
                index: The index of the selection that the message relates to.
            """
            super().__init__()
            self.selection_list: SelectionList = selection_list
            """The option list that sent the message."""
            self.selection: Selection[MessageSelectionType] = cast(
                Selection[MessageSelectionType],
                selection_list.get_option_at_index(index),
            )
            """The highlighted selection."""
            self.selection_index: int = index
            """The index of the selection that the message relates to."""

        @property
        def control(self) -> OptionList:
            """The option list that sent the message.

            This is an alias for [`OptionMessage.option_list`][textual.widgets.OptionList.OptionMessage.option_list]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.selection_list

        def __rich_repr__(self) -> Result:
            yield "selection_list", self.selection_list
            yield "selection", self.selection
            yield "selection_index", self.selection_index

    class SelectionHighlighted(SelectionMessage):
        """Message sent when a selection is highlighted.

        Can be handled using `on_selection_list_selection_highlighted` in a subclass of
        `SelectionList` or in a parent node in the DOM.
        """

    def __init__(
        self,
        *selections: tuple[TextType, SelectionType]
        | tuple[TextType, SelectionType, bool],
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
            *[self._make_selection(selection) for selection in selections],
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._selected: dict[SelectionType, None] = {}

    def _make_selection(
        self,
        selection: tuple[TextType, SelectionType]
        | tuple[TextType, SelectionType, bool],
    ) -> Selection[SelectionType]:
        """Turn incoming selection data into a `Selection` instance.

        Args:
            selection: The selection data.

        Returns:
            An instance of a `Selection`.
        """
        if len(selection) == 3:
            label, value, selected = selection
        elif len(selection) == 2:
            label, value, selected = (*selection, False)
        else:
            # TODO: Proper error.
            raise TypeError("Wrong number of values for a selection.")
        if selected:
            self._selected[value] = None
        return Selection(label, value)

    def action_toggle(self) -> None:
        if self.highlighted is not None:
            option = self.get_option_at_index(self.highlighted)
            assert isinstance(option, Selection)
            if option.value in self._selected:
                del self._selected[option._value]
            else:
                self._selected[option._value] = None
            self._refresh_content_tracking(force=True)
            self.refresh()

    def render_line(self, y: int) -> Strip:
        """Render a line in the display.

        Args:
            y: The line to render.

        Returns:
            A `Strip` that is the line to render.
        """

        # First off, get the underlying prompt from OptionList.
        prompt = super().render_line(y)

        # If it looks like the prompt itself is actually an empty line...
        if not prompt:
            # ...get out with that. We don't need to do any more here.
            return prompt

        # We know the prompt we're going to display, what we're going to do
        # is place a CheckBox-a-like button next to it. So to start with
        # let's pull out the actual Selection we're looking at right now.
        _, scroll_y = self.scroll_offset
        selection_index = scroll_y + y
        selection = self.get_option_at_index(selection_index)
        assert isinstance(selection, Selection)

        # Figure out which component style is relevant for a checkbox on
        # this particular line.
        component_style = "selection-list--button"
        if selection.value in self._selected:
            component_style += "-selected"
        if self.highlighted == selection_index:
            component_style += "-highlighted"

        # Get the underlying style used for the prompt.
        underlying_style = next(iter(prompt)).style
        assert underlying_style is not None

        # Get the style for the button.
        button_style = self.get_component_rich_style(component_style)

        # If the button is in the unselected state, we're going to do a bit
        # of a switcharound to make it look like it's a "cutout".
        if not selection.value in self._selected:
            button_style += Style.from_color(
                self.background_colors[1].rich_color, button_style.bgcolor
            )

        # Build the style for the side characters. Note that this is
        # sensitive to the type of character used, so pay attention to
        # BUTTON_LEFT and BUTTON_RIGHT.
        side_style = Style.from_color(button_style.bgcolor, underlying_style.bgcolor)

        # At this point we should have everything we need to place a
        # "button" before the option.
        return Strip(
            [
                Segment(ToggleButton.BUTTON_LEFT, style=side_style),
                Segment(ToggleButton.BUTTON_INNER, style=button_style),
                Segment(ToggleButton.BUTTON_RIGHT, style=side_style),
                Segment(" ", style=underlying_style),
                *prompt,
            ]
        )

    def _on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        """Capture the `OptionList` highlight event and turn it into a `SelectionList` event.

        Args:
            event: The event to capture and recreate.
        """
        event.stop()
        self.post_message(self.SelectionHighlighted(self, event.option_index))
