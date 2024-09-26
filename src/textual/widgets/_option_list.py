from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Iterable, NamedTuple

import rich.repr
from rich.console import RenderableType
from rich.measure import Measurement
from rich.padding import Padding
from rich.rule import Rule
from rich.style import NULL_STYLE, Style

from textual import _widget_navigation, events
from textual._widget_navigation import Direction
from textual.binding import Binding, BindingType
from textual.cache import LRUCache
from textual.geometry import Region, Size
from textual.message import Message
from textual.reactive import reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip

if TYPE_CHECKING:
    from typing_extensions import Self, TypeAlias


class DuplicateID(Exception):
    """Raised if a duplicate ID is used when adding options to an option list."""


class OptionDoesNotExist(Exception):
    """Raised when a request has been made for an option that doesn't exist."""


class Separator:
    """Class used to add a separator to an [OptionList][textual.widgets.OptionList]."""


@rich.repr.auto
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

    def set_prompt(self, prompt: RenderableType) -> None:
        """Set the prompt for the option.

        Args:
            prompt: The new prompt for the option.
        """
        self.__prompt = prompt

    @property
    def id(self) -> str | None:
        """The optional ID for the option."""
        return self.__id

    def __rich_repr__(self) -> rich.repr.Result:
        yield "prompt", self.prompt
        yield "id", self.id, None
        yield "disabled", self.disabled, False

    def __rich__(self) -> RenderableType:
        return self.__prompt


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


OptionListContent: TypeAlias = "Option | Separator"
"""The type of an item of content in the option list.

This type represents all of the types that will be found in the list of
content of the option list after it has been processed for addition.
"""

NewOptionListContent: TypeAlias = "OptionListContent | None | RenderableType"
"""The type of a new item of option list content to be added to an option list.

This type represents all of the types that will be accepted when adding new
content to the option list. This is a superset of [`OptionListContent`][textual.types.OptionListContent].
"""


class OptionList(ScrollView, can_focus=True):
    """A vertical option list with bounce-bar highlighting."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("down", "cursor_down", "Down", show=False),
        Binding("end", "last", "Last", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("home", "first", "First", show=False),
        Binding("pagedown", "page_down", "Page down", show=False),
        Binding("pageup", "page_up", "Page up", show=False),
        Binding("up", "cursor_up", "Up", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | down | Move the highlight down. |
    | end | Move the highlight to the last option. |
    | enter | Select the current option. |
    | home | Move the highlight to the first option. |
    | pagedown | Move the highlight down a page of options. |
    | pageup | Move the highlight up a page of options. |
    | up | Move the highlight up. |
    """

    DEFAULT_CSS = """
    OptionList {
        height: auto;
        max-height: 100%;
        background: $boost;
        color: $text;
        overflow-x: hidden;
        border: tall transparent;
        padding: 0 1;
    }

    OptionList:focus {
        border: tall $accent;

    }

    OptionList > .option-list--separator {
        color: $foreground 15%;
    }

    OptionList > .option-list--option-highlighted {
        color: $text;
        text-style: bold;
    }

    OptionList:focus > .option-list--option-highlighted {
        background: $accent;
    }

    OptionList > .option-list--option-disabled {
        color: $text-disabled;
    }

    OptionList > .option-list--option-hover {
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
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "option-list--option",
        "option-list--option-disabled",
        "option-list--option-highlighted",
        "option-list--option-hover",
        "option-list--option-hover-highlighted",
        "option-list--separator",
    }
    """
    | Class | Description |
    | :- | :- |
    | `option-list--option-disabled` | Target disabled options. |
    | `option-list--option-highlighted` | Target the highlighted option. |
    | `option-list--option-hover` | Target an option that has the mouse over it. |
    | `option-list--option-hover-highlighted` | Target a highlighted option that has the mouse over it. |
    | `option-list--separator` | Target the separators. |
    """

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

        def __rich_repr__(self) -> rich.repr.Result:
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
        wrap: bool = True,
        tooltip: RenderableType | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self._wrap = wrap
        """Should we auto-wrap options?

        If `False` options wider than the list will be truncated.
        """

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

        self._option_ids: dict[str, int] = {
            option.id: index
            for index, option in enumerate(self._options)
            if option.id is not None
        }
        """A dictionary of option IDs and the option indexes they relate to."""

        self._content_render_cache: LRUCache[tuple[int, Style, int], list[Strip]]
        self._content_render_cache = LRUCache(256)

        self._lines: list[tuple[int, int]] | None = None
        self._spans: list[OptionLineSpan] | None = None

        self._mouse_hovering_over: int | None = None
        """Used to track what the mouse is hovering over."""

        if tooltip is not None:
            self.tooltip = tooltip

        if self._options:
            self.action_first()

    def _left_gutter_width(self) -> int:
        """Returns the size of any left gutter that should be taken into account.

        Returns:
            The width of the left gutter.
        """
        return 0

    def _on_mount(self):
        self._populate()

    def _refresh_lines(self) -> None:
        self._lines = None
        self._spans = None
        self._content_render_cache.clear()
        self.check_idle()

    def notify_style_update(self) -> None:
        self._content_render_cache.clear()

    def _on_resize(self):
        self._refresh_lines()

    def on_idle(self):
        if self._lines is None:
            self._populate()

    def _add_lines(
        self, new_content: list[OptionListContent], width: int, option_index=0
    ) -> None:
        """Add new lines.

        Args:
            new_content: New content to add.
            width: Width to render content.
            option_index: Starting option index.
        """
        assert self._lines is not None
        assert self._spans is not None
        style = NULL_STYLE

        for index, content in enumerate(new_content, len(self._lines)):
            if isinstance(content, Option):
                height = len(
                    self._render_option_content(
                        index, content, style, width - self._left_gutter_width()
                    )
                )

                self._spans.append(OptionLineSpan(len(self._lines), height))
                self._lines.extend(
                    (option_index, y_offset) for y_offset in range(height)
                )
                option_index += 1
            else:
                self._lines.append(OptionLineSpan(-1, 0))

        self.virtual_size = Size(width, len(self._lines))

    def _populate(self) -> None:
        """Populate the lines data-structure."""
        if self._lines is not None:
            return
        self._lines = []
        self._spans = []

        self._add_lines(
            self._contents,
            self.scrollable_content_region.width - self._left_gutter_width(),
        )
        self.refresh()

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Get maximum width of options."""
        console = self.app.console
        options = console.options
        return max(
            Measurement.get(console, options, option.prompt).maximum
            for option in self._options
        )

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        # Get the content height without requiring a refresh
        # TODO: Internal data structure could be simplified
        style = self.rich_style
        _render_option_content = self._render_option_content
        heights = [
            len(_render_option_content(index, option, style, width))
            for index, option in enumerate(self._options)
        ]
        separator_count = sum(
            1 for content in self._contents if isinstance(content, Separator)
        )
        return sum(heights) + separator_count

    def _on_mouse_move(self, event: events.MouseMove) -> None:
        """React to the mouse moving.

        Args:
            event: The mouse movement event.
        """
        self._mouse_hovering_over = event.style.meta.get("option")

    def _on_leave(self, _: events.Leave) -> None:
        """React to the mouse leaving the widget."""
        self._mouse_hovering_over = None

    async def _on_click(self, event: events.Click) -> None:
        """React to the mouse being clicked on an item.

        Args:
            event: The click event.
        """
        clicked_option: int | None = event.style.meta.get("option")
        if (
            clicked_option is not None
            and clicked_option >= 0
            and not self._options[clicked_option].disabled
        ):
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

    def _render_option_content(
        self, option_index: int, renderable: RenderableType, style: Style, width: int
    ) -> list[Strip]:
        """Render content for option and style.

        Args:
            option_index: Option index to render.
            renderable: The Option renderable.
            style: The Rich style to render with.
            width: The width of the renderable.

        Returns:
            A list of strips.
        """
        cache_key = (option_index, style, width)
        if (strips := self._content_render_cache.get(cache_key, None)) is not None:
            return strips

        padding = self.get_component_styles("option-list--option").padding
        console = self.app.console
        options = console.options.update_width(width)
        if not self._wrap:
            options = options.update(no_wrap=True, overflow="ellipsis")
        if padding:
            renderable = Padding(renderable, padding)
        lines = self.app.console.render_lines(renderable, options, style=style)

        style_meta = Style.from_meta({"option": option_index})
        strips = [Strip(line, width).apply_style(style_meta) for line in lines]

        self._content_render_cache[cache_key] = strips
        return strips

    def _duplicate_id_check(self, candidate_items: list[OptionListContent]) -> None:
        """Check the items to be added for any duplicates.

        Args:
            candidate_items: The items that are going be added.

        Raises:
            DuplicateID: If there is an attempt to use a duplicate ID.
        """
        # We're only interested in options, and only those that have IDs.
        new_options = [
            item
            for item in candidate_items
            if isinstance(item, Option) and item.id is not None
        ]
        # Get the set of new IDs that we're being given.
        new_option_ids = {option.id for option in new_options}
        # Now check for duplicates, both internally amongst the new items
        # incoming, and also against all the current known IDs.
        if len(new_options) != len(new_option_ids) or not new_option_ids.isdisjoint(
            self._option_ids
        ):
            raise DuplicateID("Attempt made to add options with duplicate IDs.")

    def add_options(self, items: Iterable[NewOptionListContent]) -> Self:
        """Add new options to the end of the option list.

        Args:
            items: The new items to add.

        Returns:
            The `OptionList` instance.

        Raises:
            DuplicateID: If there is an attempt to use a duplicate ID.

        Note:
            All options are checked for duplicate IDs *before* any option is
            added. A duplicate ID will cause none of the passed items to be
            added to the option list.
        """
        # Only work if we have items to add; but don't make a fuss out of
        # zero items to add, just carry on like nothing happened.
        if self._lines is None:
            self._lines = []
        if self._spans is None:
            self._spans = []
        new_items = list(items)
        if new_items:
            option_index = len(self._options)
            # Turn any incoming values into valid content for the list.
            content = [self._make_content(item) for item in new_items]
            self._duplicate_id_check(content)
            self._contents.extend(content)
            # Pull out the content that is genuine options, create any new
            # ID mappings required, then add the new options to the option
            # list.
            new_options = [item for item in content if isinstance(item, Option)]
            for new_option_index, new_option in enumerate(
                new_options, start=len(self._options)
            ):
                if new_option.id:
                    self._option_ids[new_option.id] = new_option_index
            self._options.extend(new_options)

            self._add_lines(
                content,
                self.scrollable_content_region.width - self._left_gutter_width(),
                option_index=option_index,
            )
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
        # Decrement index of options after the one we just removed.
        self._option_ids = {
            option_id: option_index - 1 if option_index > index else option_index
            for option_id, option_index in self._option_ids.items()
            if option_index != index
        }
        self._refresh_lines()
        # Force a re-validation of the highlight.
        self.highlighted = self.highlighted
        self._mouse_hovering_over = None

    def remove_option(self, option_id: str) -> Self:
        """Remove the option with the given ID.

        Args:
            option_id: The ID of the option to remove.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        self._remove_option(self.get_option_index(option_id))
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
                f"There is no option with an index of {index!r}"
            ) from None
        return self

    def _replace_option_prompt(self, index: int, prompt: RenderableType) -> None:
        """Replace the prompt of an option in the list.

        Args:
            index: The index of the option to replace the prompt of.
            prompt: The new prompt for the option.

        Raises:
            OptionDoesNotExist: If there is no option with the given index.
        """
        self.get_option_at_index(index).set_prompt(prompt)
        self._refresh_lines()

    def replace_option_prompt(self, option_id: str, prompt: RenderableType) -> Self:
        """Replace the prompt of the option with the given ID.

        Args:
            option_id: The ID of the option to replace the prompt of.
            prompt: The new prompt for the option.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        self._replace_option_prompt(self.get_option_index(option_id), prompt)
        return self

    def replace_option_prompt_at_index(
        self, index: int, prompt: RenderableType
    ) -> Self:
        """Replace the prompt of the option at the given index.

        Args:
            index: The index of the option to replace the prompt of.
            prompt: The new prompt for the option.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If there is no option with the given index.
        """
        self._replace_option_prompt(index, prompt)
        return self

    def clear_options(self) -> Self:
        """Clear the content of the option list.

        Returns:
            The `OptionList` instance.
        """
        self._contents.clear()
        self._options.clear()
        self._option_ids.clear()
        self.highlighted = None
        self._mouse_hovering_over = None
        self._refresh_lines()
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
        if index == self.highlighted:
            self.highlighted = _widget_navigation.find_next_enabled(
                self._options, anchor=index, direction=1
            )
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
        return self.enable_option_at_index(self.get_option_index(option_id))

    def disable_option(self, option_id: str) -> Self:
        """Disable the option with the given ID.

        Args:
            option_id: The ID of the option to disable.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        return self.disable_option_at_index(self.get_option_index(option_id))

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
            OptionDoesNotExist: If there is no option with the given index.
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
            option_id: The ID of the option to get.

        Returns:
            The option with the ID.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        return self.get_option_at_index(self.get_option_index(option_id))

    def get_option_index(self, option_id: str) -> int:
        """Get the index of the option with the given ID.

        Args:
            option_id: The ID of the option to get the index of.

        Returns:
            The index of the item with the given ID.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        try:
            return self._option_ids[option_id]
        except KeyError:
            raise OptionDoesNotExist(
                f"There is no option with an ID of '{option_id}'"
            ) from None

    def render_line(self, y: int) -> Strip:
        self._populate()
        assert self._lines is not None

        _scroll_x, scroll_y = self.scroll_offset
        line_number = scroll_y + y

        try:
            option_index, y_offset = self._lines[line_number]
        except IndexError:
            return Strip([])

        renderable = (
            Rule(style=self.get_component_rich_style("option-list--separator"))
            if option_index == -1
            else self._options[option_index]
        )

        mouse_over = self._mouse_hovering_over == option_index

        component_class: str | None = None

        if option_index == -1:
            component_class = "option-list--separator"
        else:
            try:
                option = self._options[option_index]
            except IndexError:
                pass
            else:
                if option.disabled:
                    component_class = "option-list--option-disabled"
                elif self.highlighted == option_index:
                    component_class = "option-list--option-highlighted"
                elif mouse_over:
                    component_class = "option-list--option-hover"

        style = (
            self.get_component_rich_style(component_class)
            if component_class
            else self.rich_style
        )

        strips = self._render_option_content(
            option_index,
            renderable,
            style,
            self.scrollable_content_region.width - self._left_gutter_width(),
        )
        try:
            strip = strips[y_offset]
        except IndexError:
            return Strip([])
        return strip

    def scroll_to_highlight(self, top: bool = False) -> None:
        """Ensure that the highlighted option is in view.

        Args:
            top: Scroll highlight to top of the list.
        """
        highlighted = self.highlighted
        if highlighted is None or self._spans is None:
            return

        try:
            y, height = self._spans[highlighted]
        except IndexError:
            # Index error means we're being asked to scroll to a highlight
            # before all the tracking information has been worked out.
            # That's fine; let's just NoP that.
            return
        self.scroll_to_region(
            Region(0, y, self.scrollable_content_region.width, height),
            force=True,
            animate=False,
            top=top,
        )

    def validate_highlighted(self, highlighted: int | None) -> int | None:
        """Validate the `highlighted` property value on access."""
        if highlighted is None or not self._options:
            return None
        elif highlighted < 0:
            return 0
        elif highlighted >= len(self._options):
            return len(self._options) - 1

        return highlighted

    def watch_highlighted(self, highlighted: int | None) -> None:
        """React to the highlighted option having changed."""
        if highlighted is not None and not self._options[highlighted].disabled:
            self.scroll_to_highlight()
            self.post_message(self.OptionHighlighted(self, highlighted))

    def action_cursor_up(self) -> None:
        """Move the highlight up to the previous enabled option."""
        self.highlighted = _widget_navigation.find_next_enabled(
            self._options,
            anchor=self.highlighted,
            direction=-1,
        )

    def action_cursor_down(self) -> None:
        """Move the highlight down to the next enabled option."""
        self.highlighted = _widget_navigation.find_next_enabled(
            self._options,
            anchor=self.highlighted,
            direction=1,
        )

    def action_first(self) -> None:
        """Move the highlight to the first enabled option."""
        self.highlighted = _widget_navigation.find_first_enabled(self._options)

    def action_last(self) -> None:
        """Move the highlight to the last enabled option."""
        self.highlighted = _widget_navigation.find_last_enabled(self._options)

    def _page(self, direction: Direction) -> None:
        """Move the highlight roughly by one page in the given direction.

        The highlight will tentatively move by exactly one page.
        If this would result in highlighting a disabled option, instead we look for
        an enabled option "further down" the list of options.
        If there are no such enabled options, we fallback to the "last" enabled option.
        (The meaning of "further down" and "last" depend on the direction specified.)

        Args:
            direction: The direction to head, -1 for up and 1 for down.
        """

        # If we find ourselves in a position where we don't know where we're
        # going, we need a fallback location. Where we go will depend on the
        # direction.
        self._populate()
        assert self._spans is not None
        assert self._lines is not None

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
                target_option: int | None = self._lines[target_line][0]
            except IndexError:
                # An index error suggests we've gone out of bounds, let's
                # settle on whatever the call thinks is a good place to wrap
                # to.
                fallback()
            else:
                # Looks like we've figured where we'd like to jump to, we
                # just need to make sure we jump to an option that's enabled.
                if target_option is not None:
                    target_option = _widget_navigation.find_next_enabled_no_wrap(
                        candidates=self._options,
                        anchor=target_option,
                        direction=direction,
                        with_anchor=True,
                    )
                    # If we couldn't find an enabled option that's at least one page
                    # away from the current one, we instead move less than one page
                    # to the last enabled option in the correct direction.
                    if target_option is None:
                        fallback()
                    else:
                        self.highlighted = target_option

    def action_page_up(self) -> None:
        """Move the highlight up roughly by one page."""
        self._page(-1)

    def action_page_down(self) -> None:
        """Move the highlight down roughly by one page."""
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


if __name__ == "__main__":
    from textual.app import App, ComposeResult

    class OptionApp(App):
        def compose(self) -> ComposeResult:
            yield OptionList("Foo", "Bar", "Baz")

    app = OptionApp()
    app.run()
