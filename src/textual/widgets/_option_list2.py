from __future__ import annotations

from typing import ClassVar

import rich.repr
from rich.console import RenderableType
from rich.measure import Measurement
from rich.rule import Rule
from rich.style import NULL_STYLE, Style
from typing_extensions import TypeAlias

from .. import _widget_navigation, events
from ..binding import Binding, BindingType
from ..cache import LRUCache
from ..geometry import Size
from ..message import Message
from ..reactive import reactive
from ..scroll_view import ScrollView
from ..strip import Strip


class DuplicateID(Exception):
    """Raised if a duplicate ID is used when adding options to an option list."""


class OptionDoesNotExist(Exception):
    """Raised when a request has been made for an option that doesn't exist."""


class Separator:
    """Class used to add a separator to an [OptionList][textual.widgets.OptionList]."""

    def __rich__(self):
        return Rule()


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
            option.id: index for index, option in enumerate(self._options) if option.id
        }
        """A dictionary of option IDs and the option indexes they relate to."""

        self._content_render_cache: LRUCache[tuple[int, Style, int], list[Strip]] = (
            LRUCache(256)
        )

        self._lines: list[tuple[int, int]] | None = None

        self._mouse_hovering_over: int | None = None
        """Used to track what the mouse is hovering over."""

        if tooltip is not None:
            self.tooltip = tooltip

        self.action_first()

    def _left_gutter_width(self) -> int:
        """Returns the size of any left gutter that should be taken into account.

        Returns:
            The width of the left gutter.
        """
        return 0

    def _on_mount(self):
        self._populate()

    def _on_resize(self):
        self._lines = None
        self._populate()

    def _populate(self) -> None:
        if self._lines is not None:
            return
        self._lines = []
        style = Style()
        width = self.size.width

        for index, content in enumerate(self._contents):
            if isinstance(content, Option):
                height = len(self._render_option_content(index, content, style, width))
                self._lines.extend((index, y) for y in range(height))
            else:
                self._lines.append((-1, 0))

        self.virtual_size = Size(width, len(self._lines))

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Get maximum width of options."""
        console = self.app.console
        options = console.options
        return max(
            Measurement.get(console, options, option.prompt).maximum
            for option in self._options
        )

    def _on_mouse_move(self, event: events.MouseMove) -> None:
        """React to the mouse moving.

        Args:
            event: The mouse movement event.
        """
        self._mouse_hovering_over = event.style.meta.get("option")

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
        cache_key = (option_index, style, width)
        if (strips := self._content_render_cache.get(cache_key, None)) is not None:
            return strips
        console = self.app.console
        options = console.options.update_width(width)
        lines = self.app.console.render_lines(renderable, options, style=style)

        style_meta = Style.from_meta({"option": option_index})
        strips = [Strip(line, width).apply_style(style_meta) for line in lines]
        self._content_render_cache[cache_key] = strips
        return strips

    def render_line(self, y: int) -> Strip:
        self._populate()

        scroll_x, scroll_y = self.scroll_offset
        line_number = scroll_y + y

        try:
            option_index, y_offset = self._lines[line_number]
        except IndexError:
            return Strip([])

        mouse_over = self._mouse_hovering_over == option_index

        component_class: str | None = None

        if option_index == -1:
            component_class = "option-list--separator"
        else:
            option = self._options[option_index]
            if option.disabled:
                component_class = "option-list--option-disabled"
            elif self.highlighted == option_index:
                component_class = "option-list--option-highlighted"
            elif mouse_over:
                component_class = "option-list--option-hover"

        # if option_index == -1:
        #     component_classes.append("option-list--separator")
        # else:
        #     option = self._options[option_index]
        #     if option.disabled:
        #         component_classes.append("option-list--option-disabled")
        #     else:
        #         if option_index == self._mouse_hovering_over:
        #             component_classes.append("option-list--option-hover-highlighted")

        # if mouse_over is not None:
        #     component_classes.append("option-list--option-hover")

        renderable = Rule() if option_index == -1 else self._contents[option_index]

        style = (
            self.get_component_rich_style(component_class)
            if component_class
            else NULL_STYLE
        )

        strips = self._render_option_content(
            option_index, renderable, style, self.scrollable_content_region.width
        )
        strip = strips[y_offset]
        return strip

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
