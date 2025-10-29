from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Iterable, Sequence, cast

import rich.repr
from rich.segment import Segment

from textual import _widget_navigation, events
from textual._loop import loop_last
from textual.binding import Binding, BindingType
from textual.cache import LRUCache
from textual.css.styles import RulesMap
from textual.geometry import Region, Size, Spacing, clamp
from textual.message import Message
from textual.reactive import reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip
from textual.style import Style
from textual.visual import Padding, Visual, VisualType, visualize

if TYPE_CHECKING:
    from typing_extensions import Self, TypeAlias


OptionListContent: TypeAlias = "Option | VisualType | None"
"""Types accepted in OptionList constructor and [add_options()][textual.widgets.OptionList.ads_options]."""


class OptionListError(Exception):
    """An error occurred in the option list."""


class DuplicateID(OptionListError):
    """Raised if a duplicate ID is used when adding options to an option list."""


class OptionDoesNotExist(OptionListError):
    """Raised when a request has been made for an option that doesn't exist."""


@rich.repr.auto
class Option:
    """This class holds details of options in the list."""

    def __init__(
        self, prompt: VisualType, id: str | None = None, disabled: bool = False
    ) -> None:
        """Initialise the option.

        Args:
            prompt: The prompt (text displayed) for the option.
            id: An option ID for the option.
            disabled: Disable the option (will be shown grayed out, and will not be selectable).

        """
        self._prompt = prompt
        self._visual: Visual | None = None
        self._id = id
        self.disabled = disabled
        self._divider = False

    @property
    def prompt(self) -> VisualType:
        """The original prompt."""
        return self._prompt

    @property
    def id(self) -> str | None:
        """Optional ID for the option."""
        return self._id

    def _set_prompt(self, prompt: VisualType) -> None:
        """Update the prompt.

        Args:
            prompt: New prompt.

        """
        self._prompt = prompt
        self._visual = None

    def __hash__(self) -> int:
        return id(self)

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._prompt
        yield "id", self._id, None
        yield "disabled", self.disabled, False
        yield "_divider", self._divider, False


@dataclass
class _LineCache:
    """Cached line information."""

    lines: list[tuple[int, int]] = field(default_factory=list)
    heights: dict[int, int] = field(default_factory=dict)
    index_to_line: dict[int, int] = field(default_factory=dict)

    def clear(self) -> None:
        """Reset all caches."""
        self.lines.clear()
        self.heights.clear()
        self.index_to_line.clear()


class OptionList(ScrollView, can_focus=True):
    """A navigable list of options."""

    ALLOW_SELECT = False
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("down", "cursor_down", "Down", show=False),
        Binding("end", "last", "Last", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("home", "first", "First", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
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
        color: $foreground;
        overflow-x: hidden;
        border: tall $border-blurred;
        padding: 0 1;
        background: $surface;
        &.-textual-compact {
            border: none !important;
            padding: 0;
            & > .option-list--option {
                padding: 0;
            }
        }
        & > .option-list--option-highlighted {
            color: $block-cursor-blurred-foreground;
            background: $block-cursor-blurred-background;
            text-style: $block-cursor-blurred-text-style;
        }
        &:focus {
            border: tall $border;
            background-tint: $foreground 5%;
            & > .option-list--option-highlighted {
                color: $block-cursor-foreground;
                background: $block-cursor-background;
                text-style: $block-cursor-text-style;
            }
        }
        & > .option-list--separator {
            color: $foreground 15%;
        }
        & > .option-list--option-highlighted {
            color: $foreground;
            background: $block-cursor-blurred-background;
        }
        & > .option-list--option-disabled {
            color: $text-disabled;
        }
        & > .option-list--option-hover {
            background: $block-hover-background;
        }
    }
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "option-list--option",
        "option-list--option-disabled",
        "option-list--option-highlighted",
        "option-list--option-hover",
        "option-list--separator",
    }
    """
    | Class | Description |
    | :- | :- |
    | `option-list--option` | Target options that are not disabled, highlighted or have the mouse over them. |
    | `option-list--option-disabled` | Target disabled options. |
    | `option-list--option-highlighted` | Target the highlighted option. |
    | `option-list--option-hover` | Target an option that has the mouse over it. |
    | `option-list--separator` | Target the separators. |
    """

    highlighted: reactive[int | None] = reactive(None)
    """The index of the currently-highlighted option, or `None` if no option is highlighted."""

    _mouse_hovering_over: reactive[int | None] = reactive(None)
    """The index of the option under the mouse or `None`."""

    compact: reactive[bool] = reactive(False, toggle_class="-textual-compact")
    """Enable compact display?"""

    class OptionMessage(Message):
        """Base class for all option messages."""

        def __init__(self, option_list: OptionList, option: Option, index: int) -> None:
            """Initialise the option message.

            Args:
                option_list: The option list that owns the option.
                index: The index of the option that the message relates to.
            """
            super().__init__()
            self.option_list: OptionList = option_list
            """The option list that sent the message."""
            self.option: Option = option
            """The highlighted option."""
            self.option_id: str | None = option.id
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
            try:
                yield "option_list", self.option_list
                yield "option", self.option
                yield "option_id", self.option_id
                yield "option_index", self.option_index
            except AttributeError:
                return

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
        *content: OptionListContent,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        markup: bool = True,
        compact: bool = False,
    ):
        """Initialize an OptionList.

        Args:
            *content: Positional arguments become the options.
            name: Name of the OptionList.
            id: The ID of the OptionList in the DOM.
            classes: Initial CSS classes.
            disabled: Disable the widget?
            markup: Strips should be rendered as content markup if `True`, or plain text if `False`.
            compact: Enable compact style?
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._markup = markup
        self.compact = compact
        self._options: list[Option] = []
        """List of options."""
        self._id_to_option: dict[str, Option] = {}
        """Maps an Options's ID on to the option itself."""
        self._option_to_index: dict[Option, int] = {}
        """Maps an Option to it's index in self._options."""

        self._option_render_cache: LRUCache[tuple[Option, Style, Spacing], list[Strip]]
        self._option_render_cache = LRUCache(maxsize=1024 * 2)
        """Caches rendered options."""

        self._line_cache = _LineCache()
        """Used to cache additional information that can be recomputed."""

        self.add_options(content)
        if self._options:
            # TODO: Inherited from previous version. Do we always want this?
            self.action_first()

    @property
    def options(self) -> Sequence[Option]:
        """Sequence of options in the OptionList.

        !!! note "This is read-only"

        """
        return self._options

    @property
    def option_count(self) -> int:
        """The number of options."""
        return len(self._options)

    @property
    def highlighted_option(self) -> Option | None:
        """The currently highlighted option, or `None` if no option is highlighted.

        Returns:
            An Option, or `None`.
        """
        if self.highlighted is not None:
            return self.options[self.highlighted]
        else:
            return None

    def clear_options(self) -> Self:
        """Clear the content of the option list.

        Returns:
            The `OptionList` instance.
        """
        self._options.clear()
        self._line_cache.clear()
        self._option_render_cache.clear()
        self._id_to_option.clear()
        self._option_to_index.clear()
        self.highlighted = None
        self.refresh()
        self.scroll_y = 0
        self._update_lines()
        return self

    def set_options(self, options: Iterable[OptionListContent]) -> Self:
        """Set options, potentially clearing existing options.

        Args:
            options: Options to set.

        Returns:
            The `OptionList` instance.
        """
        self._options.clear()
        self._line_cache.clear()
        self._option_render_cache.clear()
        self._id_to_option.clear()
        self._option_to_index.clear()
        self.highlighted = None
        self.scroll_y = 0
        self.add_options(options)
        return self

    def add_options(self, new_options: Iterable[OptionListContent]) -> Self:
        """Add new options.

        Args:
            new_options: Content of new options.

        Returns:
            The `OptionList` instance.
        """

        new_options = list(new_options)

        option_ids = [
            option._id
            for option in new_options
            if isinstance(option, Option) and option._id is not None
        ]
        if len(option_ids) != len(set(option_ids)):
            raise DuplicateID(
                "New options contain duplicated IDs; Ensure that the IDs are unique."
            )

        if not new_options:
            return self
        if new_options[0] is None:
            # Handle the case where the first new option is None,
            # which would update the previous option.
            # This is sub-optimal, but hopefully not a common occurrence
            self._clear_caches()
        options = self._options
        add_option = self._options.append

        for prompt in new_options:
            if isinstance(prompt, Option):
                option = prompt
            elif prompt is None:
                if options:
                    options[-1]._divider = True
                continue
            else:
                option = Option(prompt)
            self._option_to_index[option] = len(options)
            if option._id is not None:
                if option._id in self._id_to_option:
                    raise DuplicateID(f"Unable to add {option!r} due to duplicate ID")
                self._id_to_option[option._id] = option
            add_option(option)
        if self.is_mounted:
            self.refresh(layout=self.styles.auto_dimensions)
            self._update_lines()
        return self

    def add_option(self, option: Option | VisualType | None = None) -> Self:
        """Add a new option to the end of the option list.

        Args:
            option: New option to add, or `None` for a separator.

        Returns:
            The `OptionList` instance.

        Raises:
            DuplicateID: If there is an attempt to use a duplicate ID.
        """
        self.add_options([option])
        return self

    def get_option(self, option_id: str) -> Option:
        """Get the option with the given ID.

        Args:
            option_id: The ID of the option to get.

        Returns:
            The option with the ID.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        try:
            return self._id_to_option[option_id]
        except KeyError:
            raise OptionDoesNotExist(
                f"There is no option with an ID of {option_id!r}"
            ) from None

    def get_option_index(self, option_id: str) -> int:
        """Get the index (offset in `self.options`) of the option with the given ID.

        Args:
            option_id: The ID of the option to get the index of.

        Returns:
            The index of the item with the given ID.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        option = self.get_option(option_id)
        return self._option_to_index[option]

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

    def _remove_option(self, option: Option) -> Self:
        """Remove the option with the given ID.

        Args:
            option: The Option to return.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """

        index = self._option_to_index[option]
        self._mouse_hovering_over = None
        self._pre_remove_option(option, index)
        for option in self.options[index + 1 :]:
            current_index = self._option_to_index[option]
            self._option_to_index[option] = current_index - 1

        option = self._options[index]
        del self._options[index]
        if option._id is not None:
            del self._id_to_option[option._id]
        del self._option_to_index[option]
        self.highlighted = self.highlighted
        self._clear_caches()
        return self

    def _pre_remove_option(self, option: Option, index: int) -> None:
        """Hook called prior to removing an option.

        Args:
            option: Option being removed.
            index: Index of option being removed.

        """

    def remove_option(self, option_id: str) -> Self:
        """Remove the option with the given ID.

        Args:
            option_id: The ID of the option to remove.

        Returns:
            The `OptionList` instance.

        Raises:
            OptionDoesNotExist: If no option has the given ID.
        """
        option = self.get_option(option_id)
        return self._remove_option(option)

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
            option = self._options[index]
        except IndexError:
            raise OptionDoesNotExist(
                f"Unable to remove; there is no option at index {index}"
            ) from None
        return self._remove_option(option)

    def _replace_option_prompt(self, index: int, prompt: VisualType) -> None:
        """Replace the prompt of an option in the list.

        Args:
            index: The index of the option to replace the prompt of.
            prompt: The new prompt for the option.

        Raises:
            OptionDoesNotExist: If there is no option with the given index.
        """
        self.get_option_at_index(index)._set_prompt(prompt)
        self._clear_caches()

    def replace_option_prompt(self, option_id: str, prompt: VisualType) -> Self:
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

    def replace_option_prompt_at_index(self, index: int, prompt: VisualType) -> Self:
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

    @property
    def _lines(self) -> Sequence[tuple[int, int]]:
        """A sequence of pairs of ints for each line, used internally.

        The first int is the index of the option, and second is the line offset.

        !!! note "This is read-only"

        Returns:
            A sequence of tuples.
        """
        self._update_lines()
        return self._line_cache.lines

    @property
    def _heights(self) -> dict[int, int]:
        self._update_lines()
        return self._line_cache.heights

    @property
    def _index_to_line(self) -> dict[int, int]:
        self._update_lines()
        return self._line_cache.index_to_line

    def _clear_caches(self) -> None:
        self._option_render_cache.clear()
        self._line_cache.clear()
        self.refresh()

    def notify_style_update(self) -> None:
        self.refresh()
        super().notify_style_update()

    def _on_resize(self):
        self._clear_caches()

    def on_show(self) -> None:
        self.scroll_to_highlight()

    def on_mount(self) -> None:
        self._update_lines()

    async def _on_click(self, event: events.Click) -> None:
        """React to the mouse being clicked on an item.

        Args:
            event: The click event.
        """
        clicked_option: int | None = event.style.meta.get("option")
        if clicked_option is not None and not self._options[clicked_option].disabled:
            self.highlighted = clicked_option
            self.action_select()

    def _get_left_gutter_width(self) -> int:
        """Returns the size of any left gutter that should be taken into account.

        Returns:
            The width of the left gutter.
        """
        return 0

    def _on_mouse_move(self, event: events.MouseMove) -> None:
        """React to the mouse moving.

        Args:
            event: The mouse movement event.
        """
        self._mouse_hovering_over = event.style.meta.get("option")

    def _on_leave(self, _: events.Leave) -> None:
        """React to the mouse leaving the widget."""
        self._mouse_hovering_over = None

    def _get_visual(self, option: Option) -> Visual:
        """Get a visual for the given option.

        Args:
            option: An option.

        Returns:
            A Visual.

        """
        if (visual := option._visual) is None:
            visual = visualize(self, option.prompt, markup=self._markup)
            option._visual = visual
        return visual

    def _get_visual_from_index(self, index: int) -> Visual:
        """Get a visual from the given index.

        Args:
            index: An index (offset in self.options).

        Returns:
            A Visual.
        """
        option = self.get_option_at_index(index)
        return self._get_visual(option)

    def _get_option_render(self, option: Option, style: Style) -> list[Strip]:
        """Get rendered option with a given style.

        Args:
            option: An option.
            style: Style of render.

        Returns:
            A list of strips.
        """
        padding = self.get_component_styles("option-list--option").padding
        render_width = self.scrollable_content_region.width
        width = render_width - self._get_left_gutter_width()
        cache_key = (option, style, padding)
        if (strips := self._option_render_cache.get(cache_key)) is None:
            visual = self._get_visual(option)
            if padding:
                visual = Padding(visual, padding)
            strips = visual.to_strips(self, visual, width, None, style)
            meta = {"option": self._option_to_index[option]}
            strips = [
                strip.extend_cell_length(width, style.rich_style).apply_meta(meta)
                for strip in strips
            ]
            if option._divider:
                style = self.get_visual_style("option-list--separator")
                rule_segments = [Segment("─" * width, style.rich_style)]
                strips.append(Strip(rule_segments, width))
            self._option_render_cache[cache_key] = strips
        return strips

    def _update_lines(self) -> None:
        """Update internal structures when new lines are added."""
        if not self.scrollable_content_region:
            return

        line_cache = self._line_cache
        lines = line_cache.lines
        next_index = lines[-1][0] + 1 if lines else 0
        get_visual = self._get_visual
        width = self.scrollable_content_region.width - self._get_left_gutter_width()

        if next_index < len(self.options):
            padding = self.get_component_styles("option-list--option").padding
            for index, option in enumerate(self.options[next_index:], next_index):
                line_cache.index_to_line[index] = len(line_cache.lines)
                line_count = (
                    get_visual(option).get_height(self.styles, width - padding.width)
                    + option._divider
                )
                line_cache.heights[index] = line_count
                line_cache.lines.extend(
                    [(index, line_no) for line_no in range(0, line_count)]
                )

        last_divider = self.options and self.options[-1]._divider
        virtual_size = Size(width, len(lines) - (1 if last_divider else 0))
        if virtual_size != self.virtual_size:
            self.virtual_size = virtual_size
            self._scroll_update(virtual_size)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Get maximum width of options."""
        if not self.options:
            return 0
        styles = self.styles
        get_visual_from_index = self._get_visual_from_index
        padding = self.get_component_styles("option-list--option").padding
        gutter_width = self._get_left_gutter_width()
        container_width = container.width
        width = (
            max(
                get_visual_from_index(index).get_optimal_width(styles, container_width)
                for index in range(len(self.options))
            )
            + padding.width
            + gutter_width
        )
        return width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Get height for the given width."""
        styles = self.styles
        rules = cast(RulesMap, styles)
        padding_width = self.get_component_styles("option-list--option").padding.width
        get_visual = self._get_visual
        height = sum(
            (
                get_visual(option).get_height(rules, width - padding_width)
                + (1 if option._divider and not last else 0)
            )
            for last, option in loop_last(self.options)
        )
        return height

    def _get_line(self, style: Style, y: int) -> Strip:
        index, line_offset = self._lines[y]
        option = self.get_option_at_index(index)
        strips = self._get_option_render(option, style)
        return strips[line_offset]

    def render_lines(self, crop: Region) -> list[Strip]:
        self._update_lines()
        return super().render_lines(crop)

    def render_line(self, y: int) -> Strip:
        line_number = self.scroll_offset.y + y
        try:
            option_index, line_offset = self._lines[line_number]
            option = self.options[option_index]
        except IndexError:
            return Strip.blank(
                self.scrollable_content_region.width,
                self.get_visual_style("option-list--option").rich_style,
            )

        mouse_over = self._mouse_hovering_over == option_index
        component_class = ""
        if option.disabled:
            component_class = "option-list--option-disabled"
        elif self.highlighted == option_index:
            component_class = "option-list--option-highlighted"
        elif mouse_over:
            component_class = "option-list--option-hover"

        if component_class:
            style = self.get_visual_style("option-list--option", component_class)
        else:
            style = self.get_visual_style("option-list--option")

        strips = self._get_option_render(option, style)
        try:
            strip = strips[line_offset]
        except IndexError:
            return Strip.blank(
                self.scrollable_content_region.width,
                self.get_visual_style("option-list--option").rich_style,
            )
        return strip

    def validate_highlighted(self, highlighted: int | None) -> int | None:
        """Validate the `highlighted` property value on access."""
        if highlighted is None or not self.options:
            return None
        elif highlighted < 0:
            return 0
        elif highlighted >= len(self.options):
            return len(self.options) - 1
        return highlighted

    def watch_highlighted(self, highlighted: int | None) -> None:
        """React to the highlighted option having changed."""
        if highlighted is None:
            return
        if not self._options[highlighted].disabled:
            self.scroll_to_highlight()
            self.post_message(
                self.OptionHighlighted(self, self.options[highlighted], highlighted)
            )

    def scroll_to_highlight(self, top: bool = False) -> None:
        """Scroll to the highlighted option.

        Args:
            top: Ensure highlighted option is at the top of the widget.
        """
        highlighted = self.highlighted
        if highlighted is None or not self.is_mounted:
            return

        self._update_lines()

        try:
            y = self._index_to_line[highlighted]
        except KeyError:
            return
        height = self._heights[highlighted]

        self.scroll_to_region(
            Region(0, y, self.scrollable_content_region.width, height),
            force=True,
            animate=False,
            top=top,
            immediate=True,
        )

    def action_cursor_up(self) -> None:
        """Move the highlight up to the previous enabled option."""
        self.highlighted = _widget_navigation.find_next_enabled(
            self.options,
            anchor=self.highlighted,
            direction=-1,
        )

    def action_cursor_down(self) -> None:
        """Move the highlight down to the next enabled option."""
        self.highlighted = _widget_navigation.find_next_enabled(
            self.options,
            anchor=self.highlighted,
            direction=1,
        )

    def action_first(self) -> None:
        """Move the highlight to the first enabled option."""
        self.highlighted = _widget_navigation.find_first_enabled(self.options)

    def action_last(self) -> None:
        """Move the highlight to the last enabled option."""
        self.highlighted = _widget_navigation.find_last_enabled(self.options)

    def _move_page(self, direction: _widget_navigation.Direction) -> None:
        """Move the height roughly by one page in the given direction.

        This method will attempt to avoid selecting a disabled option.

        Args:
            direction: `-1` to move up a page, `1` to move down a page.
        """
        if not self._options:
            return

        height = self.scrollable_content_region.height
        y = clamp(
            self._index_to_line[self.highlighted or 0] + direction * height,
            0,
            len(self._lines) - 1,
        )
        option_index = self._lines[y][0]
        self.highlighted = _widget_navigation.find_next_enabled_no_wrap(
            candidates=self._options,
            anchor=option_index,
            direction=direction,
            with_anchor=True,
        )

    def action_page_up(self):
        """Move the highlight up one page."""
        if self.highlighted is None:
            self.action_first()
        else:
            self._move_page(-1)

    def action_page_down(self):
        """Move the highlight down one page."""
        if self.highlighted is None:
            self.action_last()
        else:
            self._move_page(1)

    def action_select(self) -> None:
        """Select the currently highlighted option.

        If an option is selected then a
        [OptionList.OptionSelected][textual.widgets.OptionList.OptionSelected] will be posted.
        """
        highlighted = self.highlighted
        if highlighted is None:
            return
        option = self._options[highlighted]
        if highlighted is not None and not option.disabled:
            self.post_message(self.OptionSelected(self, option, highlighted))
