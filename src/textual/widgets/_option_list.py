"""Provides the core of a classic vertical bounce-bar option list.

Useful as a lightweight list view (not to be confused with ListView, which
is much richer but uses widgets for the items) and as the base for various
forms of bounce-bar menu.
"""

from __future__ import annotations

from typing import ClassVar, Iterable, NamedTuple

from rich.console import RenderableType
from rich.padding import Padding
from rich.repr import Result
from rich.rule import Rule
from rich.style import Style
from typing_extensions import Literal, Self, TypeAlias

from ..binding import Binding, BindingType
from ..events import Click, Idle, Leave, MouseMove
from ..geometry import Region, Size
from ..message import Message
from ..reactive import reactive
from ..scroll_view import ScrollView
from ..strip import Strip


class DuplicateID(Exception):
    """Exception raised if a duplicate ID is used."""


class OptionDoesNotExist(Exception):
    """Exception raised when a request has been made for an option that doesn't exist."""


class Option:
    """Class that holds the details of an individual option."""

    def __init__(
        self, prompt: RenderableType, id: str | None = None, disabled: bool = False
    ) -> None:
        """Initialise the option.

        Args:
            prompt: The prompt for the option.
            id: The optional ID for the option.
            disabled: The initial enabled/disabled state. Enabled by default.
        """
        self.__prompt = prompt
        self.__id = id
        self.disabled = disabled

    @property
    def prompt(self) -> RenderableType:
        """The prompt for the option."""
        return self.__prompt

    @property
    def id(self) -> str | None:
        """The optional ID for the option."""
        return self.__id

    def __rich_repr__(self) -> Result:
        yield "prompt", self.prompt
        yield "id", self.id, None
        yield "disabled", self.disabled, False


class Separator:
    """Class used to add a separator to an [OptionList][textual.widgets.OptionList]."""


class Line(NamedTuple):
    """Class that holds a list of segments for the line of a option."""

    segments: Strip
    """The strip of segments that make up the line."""

    option_index: int | None = None
    """The index of the [Option][textual.widgets.option_list.Option] that this line is related to.

    If the line isn't related to an option this will be `None`.
    """


class OptionLineSpan(NamedTuple):
    """Class that holds the line span information for an option.

    An [Option][textual.widgets.option_list.Option] can have a prompt that
    spans multiple lines. Also, there's no requirement that every option in
    an option list has the same span information. So this structure is used
    to track the line that an option starts on, and how many lines it
    contains.
    """

    first: int
    """The line position for the start of the option.."""
    line_count: int
    """The count of lines that make up the option."""

    def __contains__(self, line: object) -> bool:
        # For this named tuple `in` will have a very specific meaning; but
        # to keep mypy and friends happy we need to accept an object as the
        # parameter. So, let's keep the type checkers happy but only accept
        # an int.
        assert isinstance(line, int)
        return line >= self.first and line < (self.first + self.line_count)


OptionListContent: TypeAlias = "Option | Separator"
"""The type of an item of content in the option list.

This type represents all of the types that will be found in the list of
content of the option list after it has been processed for addition.
"""

NewOptionListContent: TypeAlias = "OptionListContent | None | RenderableType"
"""The type of a new item of option list content to be added to an option list.

This type represents all of the types that will be accepted when adding new
content to the option list. This is a superset of `OptionListContent`.
"""


class OptionList(ScrollView, can_focus=True):
    """A vertical option list with bounce-bar highlighting."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("down", "cursor_down", "Down", show=False),
        Binding("end", "last", "Last", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("home", "first", "First", show=False),
        Binding("page_down", "page_down", "Page Down", show=False),
        Binding("page_up", "page_up", "Page Up", show=False),
        Binding("up", "cursor_up", "Up", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | down | Move the highlight down. |
    | end | Move the highlight to the last option. |
    | enter | Select the current option. |
    | home | Move the highlight to the first option. |
    | page_down | Move the highlight down a page of options. |
    | page_up | Move the highlight up a page of options. |
    | up | Move the highlight up. |
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "option-list--option",
        "option-list--option-disabled",
        "option-list--option-highlighted",
        "option-list--option-highlighted-disabled",
        "option-list--option-hover",
        "option-list--option-hover-disabled",
        "option-list--option-hover-highlighted",
        "option-list--option-hover-highlighted-disabled",
        "option-list--separator",
    }
    """
    | Class | Description |
    | :- | :- |
    | `option-list--option-disabled` | Target disabled options. |
    | `option-list--option-highlighted` | Target the highlighted option. |
    | `option-list--option-highlighted-disabled` | Target a disabled option that is also highlighted. |
    | `option-list--option-hover` | Target an option that has the mouse over it. |
    | `option-list--option-hover-disabled` | Target a disabled option that has the mouse over it. |
    | `option-list--option-hover-highlighted` | Target a highlighted option that has the mouse over it. |
    | `option-list--option-hover-highlighted-disabled` | Target a disabled highlighted option that has the mouse over it. |
    | `option-list--separator` | Target the separators. |
    """

    DEFAULT_CSS = """
    OptionList {
        background: $panel-lighten-1;
        color: $text;
        overflow-x: hidden;
    }

    OptionList > .option-list--separator {
        color: $foreground 15%;
    }

    OptionList > .option-list--option-highlighted {
        background: $accent 50%;
        color: $text;
        text-style: bold;
    }

    OptionList:focus > .option-list--option-highlighted {
        background: $accent;
    }

    OptionList > .option-list--option-disabled {
        color: $text-disabled;
    }

    OptionList > .option-list--option-highlighted-disabled {
        color: $text-disabled;
        background: $accent 30%;
    }

    OptionList:focus > .option-list--option-highlighted-disabled {
        background: $accent 40%;
    }

    OptionList > .option-list--option-hover {
        background: $boost;
    }

    OptionList > .option-list--option-hover-disabled {
        color: $text-disabled;
        background: $boost;
    }

    OptionList > .option-list--option-hover-highlighted {
        background: $accent 60%;
        color: $text;
        text-style: bold;
    }

    OptionList:focus > .option-list--option-hover-highlighted {
        background: $accent;
        color: $text;
        text-style: bold;
    }

    OptionList > .option-list--option-hover-highlighted-disabled {
        color: $text-disabled;
        background: $accent 60%;
    }
    """
    """The default styling for an `OptionList`."""

    highlighted: reactive[int | None] = reactive["int | None"](None)
    """The index of the currently-highlighted option, or `None` if no option is highlighted."""

    class OptionMessage(Message):
        """Base class for all option messages."""

        def __init__(self, option_list: OptionList, index: int) -> None:
            """Initialise the option message.

            Args:
                option_list: The option list that owns the option.
                index: The index of the option that the message relates to.
            """
            super().__init__()
            self.option_list: OptionList = option_list
            """The option list that sent the message."""
            self.option: Option = option_list.get_option_at_index(index)
            """The highlighted option."""
            self.option_id: str | None = self.option.id
            """The ID of the option that the message relates to."""
            self.option_index: int = index
            """The index of the option that the message relates to."""

        @property
        def control(self) -> OptionList:
            """The option list that sent the message.

            This is an alias for [`OptionMessage.option_list`][textual.widgets.OptionList.OptionMessage.option_list]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.option_list

        def __rich_repr__(self) -> Result:
            yield "option_list", self.option_list
            yield "option", self.option
            yield "option_id", self.option_id
            yield "option_index", self.option_index

    class OptionHighlighted(OptionMessage):
        """Message sent when an option is highlighted.

        Can be handled using `on_option_list_option_highlighted` in a subclass of
        `OptionList` or in a parent node in the DOM.
        """

    class OptionSelected(OptionMessage):
        """Message sent when an option is selected.

        Can be handled using `on_option_list_option_selected` in a subclass of
        `OptionList` or in a parent node in the DOM.
        """

    def __init__(
        self,
        *content: NewOptionListContent,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the option list.

        Args:
            *content: The content for the option list.
            name: The name of the option list.
            id: The ID of the option list in the DOM.
            classes: The CSS classes of the option list.
            disabled: Whether the option list is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        # Internal refresh trackers. For things driven from on_idle.
        self._needs_refresh_content_tracking = False
        self._needs_to_scroll_to_highlight = False

        self._contents: list[OptionListContent] = [
            self._make_content(item) for item in content
        ]
        """A list of the content of the option list.

        This is *every* item that makes up the content of the option list;
        this includes both the options *and* the separators (and any other
        decoration we could end up adding -- although I don't anticipate
        anything else at the moment; but padding around separators could be
        a thing, perhaps).
        """

        self._options: list[Option] = [
            content for content in self._contents if isinstance(content, Option)
        ]
        """A list of the options within the option list.

        This is a list of references to just the options alone, ignoring the
        separators and potentially any other line-oriented option list
        content that isn't an option.
        """

        self._option_ids: dict[str, int] = {}
        """A dictionary of option IDs and the option indexes they relate to."""

        self._lines: list[Line] = []
        """A list of all of the individual lines that make up the option list.

        Note that the size of this list will be at least the same as the number
        of options, and actually greater if any prompt of any option is
        multiple lines.
        """

        self._spans: list[OptionLineSpan] = []
        """A list of the locations and sizes of all options in the option list.

        This will be the same size as the number of prompts; each entry in
        the list contains the line offset of the start of the prompt, and
        the count of the lines in the prompt.
        """

        # Initial calculation of the content tracking.
        self._request_content_tracking_refresh()

        self._mouse_hovering_over: int | None = None
        """Used to track what the mouse is hovering over."""

        # Finally, cause the highlighted property to settle down based on
        # the state of the option list in regard to its available options.
        # Be sure to have a look at validate_highlighted.
        self.highlighted = None

    def _request_content_tracking_refresh(
        self, rescroll_to_highlight: bool = False
    ) -> None:
        """Request that the content tracking information gets refreshed.

        Args:
            rescroll_to_highlight: Should the widget ensure the highlight is visible?

        Calling this method sets a flag to say the refresh should happen,
        and books the refresh call in for the next idle moment.
        """
        self._needs_refresh_content_tracking = True
        self._needs_to_scroll_to_highlight = rescroll_to_highlight
        self.check_idle()

    async def _on_idle(self, _: Idle) -> None:
        """Perform content tracking data refresh when idle."""
        self._refresh_content_tracking()
        if self._needs_to_scroll_to_highlight:
            self._needs_to_scroll_to_highlight = False
            self.scroll_to_highlight()

    def watch_show_vertical_scrollbar(self) -> None:
        """Handle the vertical scrollbar visibility status changing.

        `show_vertical_scrollbar` is watched because it has an impact on the
        available width in which to render the renderables that make up the
        options in the list. If a vertical scrollbar appears or disappears
        we need to recalculate all the lines that make up the list.
        """
        self._request_content_tracking_refresh()

    def _on_resize(self) -> None:
        """Refresh the layout of the renderables in the list when resized."""
        self._request_content_tracking_refresh(rescroll_to_highlight=True)

    def _on_mouse_move(self, event: MouseMove) -> None:
        """React to the mouse moving.

        Args:
            event: The mouse movement event.
        """
        self._mouse_hovering_over = event.style.meta.get("option")

    def _on_leave(self, _: Leave) -> None:
        """React to the mouse leaving the widget."""
        self._mouse_hovering_over = None

    async def _on_click(self, event: Click) -> None:
        """React to the mouse being clicked on an item.

        Args:
            event: The click event.
        """
        clicked_option = event.style.meta.get("option")
        if clicked_option is not None:
            self.highlighted = clicked_option
            self.action_select()

    def _make_content(self, content: NewOptionListContent) -> OptionListContent:
        """Convert a single item of content for the list into a content type.

        Args:
            content: The content to turn into a full option list type.

        Returns:
            The content, usable in the option list.
        """
        if isinstance(content, (Option, Separator)):
            return content
        if content is None:
            return Separator()
        return Option(content)

    def _clear_content_tracking(self) -> None:
        """Clear down the content tracking information."""
        self._lines.clear()
        self._spans.clear()
        # TODO: Having the option ID tracking be tied up with the main
        # content tracking isn't necessary. Can possibly improve this a wee
        # bit.
        self._option_ids.clear()

    def _refresh_content_tracking(self, force: bool = False) -> None:
        """Refresh the various forms of option list content tracking.

        Args:
            force: Optionally force the refresh.

        Raises:
            DuplicateID: If there is an attempt to use a duplicate ID.

        Without a `force` the refresh will only take place if it has been
        requested via `_refresh_content_tracking`.
        """

        # If we don't need to refresh, don't bother.
        if not self._needs_refresh_content_tracking and not force:
            return

        # If we don't know our own width yet, we can't sensibly work out the
        # heights of the prompts of the options yet, so let's shortcut that
        # work. We'll be back here once we know our height.
        if not self.size.width:
            return

        self._clear_content_tracking()
        self._needs_refresh_content_tracking = False

        # Set up for doing less property access work inside the loop.
        lines_from = self.app.console.render_lines
        options = self.app.console.options.update_width(
            self.scrollable_content_region.width
        )
        add_span = self._spans.append
        option_ids = self._option_ids
        add_lines = self._lines.extend

        # Create a rule that can be used as a separator.
        separator = Strip(lines_from(Rule(style=""))[0])

        # Work through each item that makes up the content of the list,
        # break out the individual lines that will be used to draw it, and
        # also set up the tracking of the actual options.
        line = 0
        option = 0
        padding = self.get_component_styles("option-list--option").padding
        for content in self._contents:
            if isinstance(content, Option):
                # The content is an option, so render out the prompt and
                # work out the lines needed to show it.
                new_lines = [
                    Line(
                        Strip(prompt_line).apply_style(Style(meta={"option": option})),
                        option,
                    )
                    for prompt_line in lines_from(
                        Padding(content.prompt, padding) if padding else content.prompt,
                        options,
                    )
                ]
                # Record the span information for the option.
                add_span(OptionLineSpan(line, len(new_lines)))
                if content.id is not None:
                    # The option has an ID set, create a mapping from that
                    # ID to the option so we can use it later.
                    if content.id in option_ids:
                        raise DuplicateID(
                            f"The option list already has an option with id '{content.id}'"
                        )
                    option_ids[content.id] = option
                option += 1
            else:
                # The content isn't an option, so it must be a separator (if
                # there were to be other non-option content for an option
                # list it's in this if/else where we'd process it).
                new_lines = [Line(separator)]
            add_lines(new_lines)
            line += len(new_lines)

        # Now that we know how many lines make up the whole content of the
        # list, set the virtual size.
        self.virtual_size = Size(self.scrollable_content_region.width, len(self._lines))

    def add_options(self, items: Iterable[NewOptionListContent]) -> Self:
        """Add new options to the end of the option list.

        Args:
            items: The new items to add.

        Returns:
            The `OptionList` instance.

        Raises:
            DuplicateID: If there is an attempt to use a duplicate ID.
        """
        # Only work if we have items to add; but don't make a fuss out of
        # zero items to add, just carry on like nothing happened.
        if items:
            # Turn any incoming values into valid content for the list.
            content = [self._make_content(item) for item in items]
            self._contents.extend(content)
            # Pull out the content that is genuine options and add them to the
            # list of options.
            self._options.extend([item for item in content if isinstance(item, Option)])
            self._refresh_content_tracking(force=True)
            self.refresh()
        return self

    def add_option(self, item: NewOptionListContent = None) -> Self:
        """Add a new option to the end of the option list.

        Args:
            item: The new item to add.

        Returns:
            The `OptionList` instance.

        Raises:
            DuplicateID: If there is an attempt to use a duplicate ID.
        """
        return self.add_options([item])

    def _remove_option(self, index: int) -> None:
        """Remove an option from the option list.

        Args:
            index: The index of the item to remove.

        Raises:
            IndexError: If there is no option of the given index.
        """
        option = self._options[index]
        del self._options[index]
        del self._contents[self._contents.index(option)]
        self._refresh_content_tracking(force=True)
        # Force a re-validation of the highlight.
        self.highlighted = self.highlighted
        self.refresh()

    def remove_option(self, option_id: str) -> Self:
        """Remove the option with the given ID.

        Args:
            option_id: The ID of the option to remove.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        try:
            self._remove_option(self._option_ids[option_id])
        except KeyError:
            raise OptionDoesNotExist(
                f"There is no option with an ID of '{option_id}'"
            ) from None
        return self

    def remove_option_at_index(self, index: int) -> Self:
        """Remove the option at the given index.

        Args:
            index: The index of the option to remove.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If there is no option with the given index.
        """
        try:
            self._remove_option(index)
        except IndexError:
            raise OptionDoesNotExist(
                f"There is no option with an index of {index}"
            ) from None
        return self

    def clear_options(self) -> Self:
        """Clear the content of the option list.

        Returns:
            The `OptionList` instance.
        """
        self._contents.clear()
        self._options.clear()
        self.highlighted = None
        self._mouse_hovering_over = None
        self.virtual_size = Size(self.scrollable_content_region.width, 0)
        # TODO: See https://github.com/Textualize/textual/issues/2582 -- it
        # should not be necessary to do this like this here; ideally here in
        # clear_options it would be a forced refresh, and also in a
        # `on_show` it would be the same (which, I think, would actually
        # solve the problem we're seeing). But, until such a time as we get
        # to the bottom of 2582... this seems to delay the refresh enough
        # that things fall into place.
        self._request_content_tracking_refresh()
        return self

    def _set_option_disabled(self, index: int, disabled: bool) -> Self:
        """Set the disabled state of an option in the list.

        Args:
            index: The index of the option to set the disabled state of.
            disabled: The disabled state to set.

        Returns:
            The `OptionList` instance.
        """
        self._options[index].disabled = disabled
        # TODO: Refresh only if the affected option is visible.
        self.refresh()
        return self

    def enable_option_at_index(self, index: int) -> Self:
        """Enable the option at the given index.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If there is no option with the given index.
        """
        try:
            return self._set_option_disabled(index, False)
        except IndexError:
            raise OptionDoesNotExist(
                f"There is no option with an index of {index}"
            ) from None

    def disable_option_at_index(self, index: int) -> Self:
        """Disable the option at the given index.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If there is no option with the given index.
        """
        try:
            return self._set_option_disabled(index, True)
        except IndexError:
            raise OptionDoesNotExist(
                f"There is no option with an index of {index}"
            ) from None

    def enable_option(self, option_id: str) -> Self:
        """Enable the option with the given ID.

        Args:
            option_id: The ID of the option to enable.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        try:
            return self.enable_option_at_index(self._option_ids[option_id])
        except KeyError:
            raise OptionDoesNotExist(
                f"There is no option with an ID of '{option_id}'"
            ) from None

    def disable_option(self, option_id: str) -> Self:
        """Disable the option with the given ID.

        Args:
            option_id: The ID of the option to disable.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        try:
            return self.disable_option_at_index(self._option_ids[option_id])
        except KeyError:
            raise OptionDoesNotExist(
                f"There is no option with an ID of '{option_id}'"
            ) from None

    @property
    def option_count(self) -> int:
        """The count of options."""
        return len(self._options)

    def get_option_at_index(self, index: int) -> Option:
        """Get the option at the given index.

        Args:
            index: The index of the option to get.

        Returns:
            The option at that index.

        Raises:
            OptionDoesNotExist: If there is no option with the index.
        """
        try:
            return self._options[index]
        except IndexError:
            raise OptionDoesNotExist(
                f"There is no option with an index of {index}"
            ) from None

    def get_option(self, option_id: str) -> Option:
        """Get the option with the given ID.

        Args:
            index: The ID of the option to get.

        Returns:
            The option at with the ID.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        try:
            return self.get_option_at_index(self._option_ids[option_id])
        except KeyError:
            raise OptionDoesNotExist(
                f"There is no option with an ID of '{option_id}'"
            ) from None

    def render_line(self, y: int) -> Strip:
        """Render a single line in the option list.

        Args:
            y: The Y offset of the line to render.

        Returns:
            A `Strip` instance for the caller to render.
        """

        scroll_x, scroll_y = self.scroll_offset

        # First off, work out which line we're working on, based off the
        # current scroll offset plus the line we're being asked to render.
        line_number = scroll_y + y
        try:
            line = self._lines[line_number]
        except IndexError:
            # An IndexError means we're drawing in an option list where
            # there's more list than there are options.
            return Strip([])

        # Now that we know which line we're on, pull out the option index so
        # we have a "local" copy to refer to rather than needing to do a
        # property access multiple times.
        option_index = line.option_index

        # Knowing which line we're going to be drawing, we can now go pull
        # the relevant segments for the line of that particular prompt.
        strip = line.segments

        # If the line we're looking at isn't associated with an option, it
        # will be a separator, so let's exit early with that.
        if option_index is None:
            return strip.apply_style(
                self.get_component_rich_style("option-list--separator")
            )

        # At this point we know we're drawing actual content. To allow for
        # horizontal scrolling, let's crop the strip at the right locations.
        strip = strip.crop(scroll_x, scroll_x + self.scrollable_content_region.width)

        highlighted = self.highlighted
        mouse_over = self._mouse_hovering_over
        spans = self._spans

        # Handle drawing a disabled option.
        if self._options[option_index].disabled:
            # Disabled but the highlight?
            if option_index == highlighted:
                return strip.apply_style(
                    self.get_component_rich_style(
                        "option-list--option-hover-highlighted-disabled"
                        if option_index == mouse_over
                        else "option-list--option-highlighted-disabled"
                    )
                )
            # Disabled but mouse hover?
            if option_index == mouse_over:
                return strip.apply_style(
                    self.get_component_rich_style("option-list--option-hover-disabled")
                )
            # Just a normal disabled option.
            return strip.apply_style(
                self.get_component_rich_style("option-list--option-disabled")
            )

        # Handle drawing a highlighted option.
        if highlighted is not None and line_number in spans[highlighted]:
            # Highlighted with the mouse over it?
            if option_index == mouse_over:
                return strip.apply_style(
                    self.get_component_rich_style(
                        "option-list--option-hover-highlighted"
                    )
                )
            # Just a normal highlight.
            return strip.apply_style(
                self.get_component_rich_style("option-list--option-highlighted")
            )

        # Perhaps the line is within an otherwise-uninteresting option that
        # has the mouse hovering over it?
        if mouse_over is not None and line_number in spans[mouse_over]:
            return strip.apply_style(
                self.get_component_rich_style("option-list--option-hover")
            )

        # It's a normal option line.
        return strip.apply_style(self.rich_style)

    def scroll_to_highlight(self, top: bool = False) -> None:
        """Ensure that the highlighted option is in view.

        Args:
            top: Scroll highlight to top of the list.

        """
        highlighted = self.highlighted
        if highlighted is None:
            return
        try:
            span = self._spans[highlighted]
        except IndexError:
            # Index error means we're being asked to scroll to a highlight
            # before all the tracking information has been worked out.
            # That's fine; let's just NoP that.
            return
        self.scroll_to_region(
            Region(
                0, span.first, self.scrollable_content_region.width, span.line_count
            ),
            force=True,
            animate=False,
            top=top,
        )

    def validate_highlighted(self, highlighted: int | None) -> int | None:
        """Validate the `highlighted` property value on access."""
        if not self._options:
            return None
        if highlighted is None or highlighted < 0:
            return 0
        return min(highlighted, len(self._options) - 1)

    def watch_highlighted(self, highlighted: int | None) -> None:
        """React to the highlighted option having changed."""
        if highlighted is not None:
            self.scroll_to_highlight()
            if not self._options[highlighted].disabled:
                self.post_message(self.OptionHighlighted(self, highlighted))

    def action_cursor_up(self) -> None:
        """Move the highlight up by one option."""
        if self.highlighted is not None:
            if self.highlighted > 0:
                self.highlighted -= 1
            else:
                self.highlighted = len(self._options) - 1
        elif self._options:
            self.action_first()

    def action_cursor_down(self) -> None:
        """Move the highlight down by one option."""
        if self.highlighted is not None:
            if self.highlighted < len(self._options) - 1:
                self.highlighted += 1
            else:
                self.highlighted = 0
        elif self._options:
            self.action_first()

    def action_first(self) -> None:
        """Move the highlight to the first option."""
        if self._options:
            self.highlighted = 0

    def action_last(self) -> None:
        """Move the highlight to the last option."""
        if self._options:
            self.highlighted = len(self._options) - 1

    def _page(self, direction: Literal[-1, 1]) -> None:
        """Move the highlight by one page.

        Args:
            direction: The direction to head, -1 for up and 1 for down.
        """

        # If we find ourselves in a position where we don't know where we're
        # going, we need a fallback location. Where we go will depend on the
        # direction.
        fallback = self.action_first if direction == -1 else self.action_last

        highlighted = self.highlighted
        if highlighted is None:
            # There is no highlight yet so let's go to the default position.
            fallback()
        else:
            # We want to page roughly by lines, but we're dealing with
            # options that can be a varying number of lines in height. So
            # let's start with the target line alone.
            target_line = max(
                0,
                self._spans[highlighted].first
                + (direction * self.scrollable_content_region.height),
            )
            try:
                # Now that we've got a target line, let's figure out the
                # index of the target option.
                target_option = self._lines[target_line].option_index
            except IndexError:
                # An index error suggests we've gone out of bounds, let's
                # settle on whatever the call things is a good place to wrap
                # to.
                fallback()
            else:
                # Looks like we've figured out the next option to jump to.
                self.highlighted = target_option

    def action_page_up(self):
        """Move the highlight up one page."""
        self._page(-1)

    def action_page_down(self):
        """Move the highlight down one page."""
        self._page(1)

    def action_select(self) -> None:
        """Select the currently-highlighted option.

        If no option is selected, then nothing happens. If an option is
        selected, a [OptionList.OptionSelected][textual.widgets.OptionList.OptionSelected]
        message will be posted.
        """
        highlighted = self.highlighted
        if highlighted is not None and not self._options[highlighted].disabled:
            self.post_message(self.OptionSelected(self, highlighted))
