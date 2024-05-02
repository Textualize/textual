"""Provides a selection list widget, allowing one or more items to be selected."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, ClassVar, Generic, Iterable, TypeVar, cast

from rich.repr import Result
from rich.segment import Segment
from rich.style import Style
from rich.text import Text, TextType
from typing_extensions import Self

from .. import events
from ..binding import Binding
from ..messages import Message
from ..strip import Strip
from ._option_list import NewOptionListContent, Option, OptionList
from ._toggle_button import ToggleButton

SelectionType = TypeVar("SelectionType")
"""The type for the value of a [`Selection`][textual.widgets.selection_list.Selection] in a [`SelectionList`][textual.widgets.SelectionList]"""

MessageSelectionType = TypeVar("MessageSelectionType")
"""The type for the value of a [`Selection`][textual.widgets.selection_list.Selection] in a [`SelectionList`][textual.widgets.SelectionList] message."""


class SelectionError(TypeError):
    """Type of an error raised if a selection is badly-formed."""


class Selection(Generic[SelectionType], Option):
    """A selection for a [`SelectionList`][textual.widgets.SelectionList]."""

    def __init__(
        self,
        prompt: TextType,
        value: SelectionType,
        initial_state: bool = False,
        id: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the selection.

        Args:
            prompt: The prompt for the selection.
            value: The value for the selection.
            initial_state: The initial selected state of the selection.
            id: The optional ID for the selection.
            disabled: The initial enabled/disabled state. Enabled by default.
        """
        if isinstance(prompt, str):
            prompt = Text.from_markup(prompt)
        super().__init__(prompt.split()[0], id, disabled)
        self._value: SelectionType = value
        """The value associated with the selection."""
        self._initial_state: bool = initial_state
        """The initial selected state for the selection."""

    @property
    def value(self) -> SelectionType:
        """The value for this selection."""
        return self._value

    @property
    def initial_state(self) -> bool:
        """The initial selected state for the selection."""
        return self._initial_state


class SelectionList(Generic[SelectionType], OptionList):
    """A vertical selection list that allows making multiple selections."""

    BINDINGS = [Binding("space", "select")]
    """
    | Key(s) | Description |
    | :- | :- |
    | space | Toggle the state of the highlighted selection. |
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "selection-list--button",
        "selection-list--button-selected",
        "selection-list--button-highlighted",
        "selection-list--button-selected-highlighted",
    }
    """
    | Class | Description |
    | :- | :- |
    | `selection-list--button` | Target the default button style. |
    | `selection-list--button-selected` | Target a selected button style. |
    | `selection-list--button-highlighted` | Target a highlighted button style. |
    | `selection-list--button-selected-highlighted` | Target a highlighted selected button style. |
    """

    DEFAULT_CSS = """
    SelectionList {
        height: auto;
    }

    SelectionList:light:focus > .selection-list--button-selected {
        color: $primary;
    }

    SelectionList:light > .selection-list--button-selected-highlighted {
        color: $primary;
    }

    SelectionList:light:focus > .selection-list--button-selected-highlighted {
        color: $primary;
    }

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
        color: $success;
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

        def __init__(
            self, selection_list: SelectionList[MessageSelectionType], index: int
        ) -> None:
            """Initialise the selection message.

            Args:
                selection_list: The selection list that owns the selection.
                index: The index of the selection that the message relates to.
            """
            super().__init__()
            self.selection_list: SelectionList[MessageSelectionType] = selection_list
            """The selection list that sent the message."""
            self.selection: Selection[MessageSelectionType] = (
                selection_list.get_option_at_index(index)
            )
            """The highlighted selection."""
            self.selection_index: int = index
            """The index of the selection that the message relates to."""

        @property
        def control(self) -> OptionList:
            """The selection list that sent the message.

            This is an alias for
            [`SelectionMessage.selection_list`][textual.widgets.SelectionList.SelectionMessage.selection_list]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.selection_list

        def __rich_repr__(self) -> Result:
            yield "selection_list", self.selection_list
            yield "selection", self.selection
            yield "selection_index", self.selection_index

    class SelectionHighlighted(SelectionMessage[MessageSelectionType]):
        """Message sent when a selection is highlighted.

        Can be handled using `on_selection_list_selection_highlighted` in a subclass of
        [`SelectionList`][textual.widgets.SelectionList] or in a parent node in the DOM.
        """

    class SelectionToggled(SelectionMessage[MessageSelectionType]):
        """Message sent when a selection is toggled.

        Can be handled using `on_selection_list_selection_toggled` in a subclass of
        [`SelectionList`][textual.widgets.SelectionList] or in a parent node in the DOM.
        """

    @dataclass
    class SelectedChanged(Generic[MessageSelectionType], Message):
        """Message sent when the collection of selected values changes.

        Can be handled using `on_selection_list_selected_changed` in a subclass of
        [`SelectionList`][textual.widgets.SelectionList] or in a parent node in the DOM.
        """

        selection_list: SelectionList[MessageSelectionType]
        """The `SelectionList` that sent the message."""

        @property
        def control(self) -> SelectionList[MessageSelectionType]:
            """An alias for `selection_list`."""
            return self.selection_list

    def __init__(
        self,
        *selections: Selection[SelectionType]
        | tuple[TextType, SelectionType]
        | tuple[TextType, SelectionType, bool],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the selection list.

        Args:
            *selections: The content for the selection list.
            name: The name of the selection list.
            id: The ID of the selection list in the DOM.
            classes: The CSS classes of the selection list.
            disabled: Whether the selection list is disabled or not.
        """
        self._selected: dict[SelectionType, None] = {}
        """Tracking of which values are selected."""
        self._send_messages = False
        """Keep track of when we're ready to start sending messages."""
        options = [self._make_selection(selection) for selection in selections]
        super().__init__(
            *options,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            wrap=False,
        )
        self._values: dict[SelectionType, int] = {
            option.value: index for index, option in enumerate(options)
        }
        """Keeps track of which value relates to which option."""

    @property
    def selected(self) -> list[SelectionType]:
        """The selected values.

        This is a list of all of the
        [values][textual.widgets.selection_list.Selection.value] associated
        with selections in the list that are currently in the selected
        state.
        """
        return list(self._selected.keys())

    def _on_mount(self, _event: events.Mount) -> None:
        """Configure the list once the DOM is ready."""
        self._send_messages = True

    def _message_changed(self) -> None:
        """Post a message that the selected collection has changed, where appropriate.

        Note:
            A message will only be sent if `_send_messages` is `True`. This
            makes this safe to call before the widget is ready for posting
            messages.
        """
        if self._send_messages:
            self.post_message(self.SelectedChanged(self).set_sender(self))

    def _message_toggled(self, option_index: int) -> None:
        """Post a message that an option was toggled, where appropriate.

        Note:
            A message will only be sent if `_send_messages` is `True`. This
            makes this safe to call before the widget is ready for posting
            messages.
        """
        if self._send_messages:
            self.post_message(
                self.SelectionToggled(self, option_index).set_sender(self)
            )

    def _apply_to_all(self, state_change: Callable[[SelectionType], bool]) -> Self:
        """Apply a selection state change to all selection options in the list.

        Args:
            state_change: The state change function to apply.

        Returns:
            The [`SelectionList`][textual.widgets.SelectionList] instance.

        Note:
            This method will post a single
            [`SelectedChanged`][textual.widgets.OptionList.SelectedChanged]
            message if a change is made in a call to this method.
        """

        # Keep track of if anything changed.
        changed = False

        # Next we run through everything and apply the change, preventing
        # the toggled and changed messages because the caller really isn't
        # going to be expecting a message storm from this.
        with self.prevent(self.SelectedChanged, self.SelectionToggled):
            for selection in self._options:
                changed = (
                    state_change(cast(Selection[SelectionType], selection).value)
                    or changed
                )

        # If the above did make a change, *then* send a message.
        if changed:
            self._message_changed()

        self.refresh()
        return self

    def _select(self, value: SelectionType) -> bool:
        """Mark the given value as selected.

        Args:
            value: The value to mark as selected.

        Returns:
            `True` if the value was selected, `False` if not.
        """
        if value not in self._selected:
            self._selected[value] = None
            self._message_changed()
            return True
        return False

    def select(self, selection: Selection[SelectionType] | SelectionType) -> Self:
        """Mark the given selection as selected.

        Args:
            selection: The selection to mark as selected.

        Returns:
            The [`SelectionList`][textual.widgets.SelectionList] instance.
        """
        if self._select(
            selection.value
            if isinstance(selection, Selection)
            else cast(SelectionType, selection)
        ):
            self.refresh()
        return self

    def select_all(self) -> Self:
        """Select all items.

        Returns:
            The [`SelectionList`][textual.widgets.SelectionList] instance.
        """
        return self._apply_to_all(self._select)

    def _deselect(self, value: SelectionType) -> bool:
        """Mark the given selection as not selected.

        Args:
            value: The value to mark as not selected.

        Returns:
            `True` if the value was deselected, `False` if not.
        """
        try:
            del self._selected[value]
        except KeyError:
            return False
        self._message_changed()
        return True

    def deselect(self, selection: Selection[SelectionType] | SelectionType) -> Self:
        """Mark the given selection as not selected.

        Args:
            selection: The selection to mark as not selected.

        Returns:
            The [`SelectionList`][textual.widgets.SelectionList] instance.
        """
        if self._deselect(
            selection.value
            if isinstance(selection, Selection)
            else cast(SelectionType, selection)
        ):
            self.refresh()
        return self

    def deselect_all(self) -> Self:
        """Deselect all items.

        Returns:
            The [`SelectionList`][textual.widgets.SelectionList] instance.
        """
        return self._apply_to_all(self._deselect)

    def _toggle(self, value: SelectionType) -> bool:
        """Toggle the selection state of the given value.

        Args:
            value: The value to toggle.

        Returns:
            `True`.
        """
        if value in self._selected:
            self._deselect(value)
        else:
            self._select(value)
        self._message_toggled(self._values[value])
        return True

    def toggle(self, selection: Selection[SelectionType] | SelectionType) -> Self:
        """Toggle the selected state of the given selection.

        Args:
            selection: The selection to toggle.

        Returns:
            The [`SelectionList`][textual.widgets.SelectionList] instance.
        """
        self._toggle(
            selection.value
            if isinstance(selection, Selection)
            else cast(SelectionType, selection)
        )
        self.refresh()
        return self

    def toggle_all(self) -> Self:
        """Toggle all items.

        Returns:
            The [`SelectionList`][textual.widgets.SelectionList] instance.
        """
        return self._apply_to_all(self._toggle)

    def _make_selection(
        self,
        selection: (
            Selection[SelectionType]
            | tuple[TextType, SelectionType]
            | tuple[TextType, SelectionType, bool]
        ),
    ) -> Selection[SelectionType]:
        """Turn incoming selection data into a `Selection` instance.

        Args:
            selection: The selection data.

        Returns:
            An instance of a `Selection`.

        Raises:
            SelectionError: If the selection was badly-formed.
        """

        # If we've been given a tuple of some sort, turn that into a proper
        # Selection.
        if isinstance(selection, tuple):
            if len(selection) == 2:
                selection = cast(
                    "tuple[TextType, SelectionType, bool]", (*selection, False)
                )
            elif len(selection) != 3:
                raise SelectionError(f"Expected 2 or 3 values, got {len(selection)}")
            selection = Selection[SelectionType](*selection)

        # At this point we should have a proper selection.
        assert isinstance(selection, Selection)

        # If the initial state for this is that it's selected, add it to the
        # selected collection.
        if selection.initial_state:
            self._select(selection.value)

        return selection

    def _toggle_highlighted_selection(self) -> None:
        """Toggle the state of the highlighted selection.

        If nothing is selected in the list this is a non-operation.
        """
        if self.highlighted is not None:
            self.toggle(self.get_option_at_index(self.highlighted))

    def _left_gutter_width(self) -> int:
        """Returns the size of any left gutter that should be taken into account.

        Returns:
            The width of the left gutter.
        """
        return len(
            ToggleButton.BUTTON_LEFT
            + ToggleButton.BUTTON_INNER
            + ToggleButton.BUTTON_RIGHT
            + " "
        )

    def render_line(self, y: int) -> Strip:
        """Render a line in the display.

        Args:
            y: The line to render.

        Returns:
            A [`Strip`][textual.strip.Strip] that is the line to render.
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
        if selection.value not in self._selected:
            button_style += Style.from_color(
                self.background_colors[1].rich_color, button_style.bgcolor
            )

        # Build the style for the side characters. Note that this is
        # sensitive to the type of character used, so pay attention to
        # BUTTON_LEFT and BUTTON_RIGHT.
        side_style = Style.from_color(button_style.bgcolor, underlying_style.bgcolor)

        # Add the option index to the style. This is used to determine which
        # option to select when the button is clicked or hovered.
        side_style += Style(meta={"option": selection_index})
        button_style += Style(meta={"option": selection_index})

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
        """Capture the `OptionList` highlight event and turn it into a [`SelectionList`][textual.widgets.SelectionList] event.

        Args:
            event: The event to capture and recreate.
        """
        event.stop()
        self.post_message(self.SelectionHighlighted(self, event.option_index))

    def _on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Capture the `OptionList` selected event and turn it into a [`SelectionList`][textual.widgets.SelectionList] event.

        Args:
            event: The event to capture and recreate.
        """
        event.stop()
        self._toggle_highlighted_selection()

    def get_option_at_index(self, index: int) -> Selection[SelectionType]:
        """Get the selection option at the given index.

        Args:
            index: The index of the selection option to get.

        Returns:
            The selection option at that index.

        Raises:
            OptionDoesNotExist: If there is no selection option with the index.
        """
        return cast("Selection[SelectionType]", super().get_option_at_index(index))

    def get_option(self, option_id: str) -> Selection[SelectionType]:
        """Get the selection option with the given ID.

        Args:
            option_id: The ID of the selection option to get.

        Returns:
            The selection option with the ID.

        Raises:
            OptionDoesNotExist: If no selection option has the given ID.
        """
        return cast("Selection[SelectionType]", super().get_option(option_id))

    def _remove_option(self, index: int) -> None:
        """Remove a selection option from the selection option list.

        Args:
            index: The index of the selection option to remove.

        Raises:
            IndexError: If there is no selection option of the given index.
        """
        option = self.get_option_at_index(index)
        self._deselect(option.value)
        del self._values[option.value]
        # Decrement index of options after the one we just removed.
        self._values = {
            option_value: option_index - 1 if option_index > index else option_index
            for option_value, option_index in self._values.items()
        }
        return super()._remove_option(index)

    def add_options(
        self,
        items: Iterable[
            NewOptionListContent
            | Selection[SelectionType]
            | tuple[TextType, SelectionType]
            | tuple[TextType, SelectionType, bool]
        ],
    ) -> Self:
        """Add new selection options to the end of the list.

        Args:
            items: The new items to add.

        Returns:
            The [`SelectionList`][textual.widgets.SelectionList] instance.

        Raises:
            DuplicateID: If there is an attempt to use a duplicate ID.
            SelectionError: If one of the selection options is of the wrong form.
        """
        # This... is sort of sub-optimal, but a natural consequence of
        # inheriting from and narrowing down OptionList. Here we don't want
        # things like a separator, or a base Option, being passed in. So we
        # extend the types of accepted items to keep mypy and friends happy,
        # but then we runtime check that we've been given sensible types (in
        # this case the supported tuple values).
        cleaned_options: list[Selection[SelectionType]] = []
        for item in items:
            if isinstance(item, tuple):
                cleaned_options.append(
                    self._make_selection(
                        cast(
                            "tuple[TextType, SelectionType] | tuple[TextType, SelectionType, bool]",
                            item,
                        )
                    )
                )
            elif isinstance(item, Selection):
                cleaned_options.append(self._make_selection(item))
            else:
                raise SelectionError(
                    "Only Selection or a prompt/value tuple is supported in SelectionList"
                )

        # Add the new items to the value mappings.
        self._values.update(
            {
                option.value: index
                for index, option in enumerate(cleaned_options, start=self.option_count)
            }
        )

        return super().add_options(cleaned_options)

    def add_option(
        self,
        item: (
            NewOptionListContent
            | Selection
            | tuple[TextType, SelectionType]
            | tuple[TextType, SelectionType, bool]
        ) = None,
    ) -> Self:
        """Add a new selection option to the end of the list.

        Args:
            item: The new item to add.

        Returns:
            The [`SelectionList`][textual.widgets.SelectionList] instance.

        Raises:
            DuplicateID: If there is an attempt to use a duplicate ID.
            SelectionError: If the selection option is of the wrong form.
        """
        return self.add_options([item])

    def clear_options(self) -> Self:
        """Clear the content of the selection list.

        Returns:
            The `SelectionList` instance.
        """
        self._selected.clear()
        self._values.clear()
        return super().clear_options()
