"""Provides the core of a classic vertical bounce-bar menu."""

from __future__ import annotations

from typing import Callable, ClassVar, Generic, Literal, NamedTuple, TypeVar

from rich.console import RenderableType
from rich.repr import Result
from rich.segment import Segment

from ..binding import Binding, BindingType
from ..geometry import Region, Size
from ..message import Message
from ..reactive import reactive
from ..scroll_view import ScrollView
from ..strip import Strip

MenuDataType = TypeVar("MenuDataType")
"""The type of the data for a given instance of a [Menu][textual.widgets.Menu]."""

MenuMessageDataType = TypeVar("MenuMessageDataType")
"""The type of the data for a given instance of a [Menu][textual.widgets.Menu].

As used when creating messages.
"""


class MenuOption(NamedTuple, Generic[MenuDataType]):
    """Class that holds the details of an individual menu option."""

    prompt: RenderableType
    """The prompt for the menu option."""
    data: MenuDataType | None = None
    """Data associated with the menu option."""


class OptionLineSegments(NamedTuple, Generic[MenuDataType]):
    """Class that holds a list of segments for the line of a menu option."""

    # TODO: I might be able to do away with option and just work with index.
    option: MenuOption[MenuDataType]
    """The [MenuOption][textual.widgets.menu.MenuOption] related to the line."""
    option_index: int
    """The index of the [MenuOption][textual.widgets.menu.MenuOption] that this line is related to."""
    segments: list[Segment]
    """The list of segments that make up the line of the prompt."""


class OptionLineSpan(NamedTuple):
    """Class that holds the line span information for a menu option."""

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


class Menu(Generic[MenuDataType], ScrollView, can_focus=True):
    """A vertical bounce-bar menu."""

    # TODO:
    #
    # Little to no regard has been given to caching and optimisation right
    # now. This is at the "get the API right" stage of things, then it'll be
    # at the "make it fast" stage.

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("up", "up", "Up", show=False),
        Binding("down", "down", "Down", show=False),
        Binding("home", "first", "First", show=False),
        Binding("end", "last", "Last", show=False),
        Binding("page_up", "page_up", "Page Up", show=False),
        Binding("page_down", "page_down", "Page Down", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | up | Move the menu highlight up. |
    | down | Move the menu highlight down. |
    | home | Move the menu highlight to the first option. |
    | end | Move the menu highlight to the last option. |
    | page_up | Move the menu highlight up a page of options. |
    | page_down | Move the menu highlight down a page of options. |
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "menu--option-highlighted",
        "menu--option-hover",
    }
    """
    | Class | Description |
    | :- | :- |
    | `menu--option-highlighted` | Target the highlighted menu option. |
    """

    DEFAULT_CSS = """
    Menu {
        overflow: hidden;
    }

    Menu > .menu--option-highlighted {
        background: $secondary-darken-2;
        color: $text;
        text-style: bold;
    }

    Menu:focus > .menu--option-highlighted {
        background: $secondary;
    }
    """

    highlighted: reactive[int | None] = reactive["int | None"](None)
    """The index of the currently-highlighted option, or `None` if no option is highlighted."""

    # TODO: REMOVE BEFORE FLIGHT!
    class Debug(Message):
        """A debug message. Remove before flight."""

        def __init__(self, cargo: object) -> None:
            super().__init__()
            self.cargo = cargo

    class OptionHighlighted(Generic[MenuMessageDataType], Message):
        """Message sent when an option is highlighted.

        Can be handled using `on_menu_option_highlighted` in a subclass of
        `Menu` or in a parent node in the DOM.
        """

        def __init__(self, menu: Menu, index: int) -> None:
            """Initialise the option highlighted message.

            Args:
                menu: The menu that has the highlighted option.
                option: The option that is highlighted.
            """
            super().__init__()
            self.menu = menu
            """The menu that sent the message."""
            self.index = index
            """The index of the highlighted option."""
            self.option = menu.option(index)
            """The highlighted option."""

        def __rich_repr__(self) -> Result:
            yield "menu", self.menu
            yield "index", self.index
            yield "option", self.option

    def __init__(
        self,
        *options: MenuOption[MenuDataType] | RenderableType,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the menu.

        Args:
            *options: The options for the menu.
            name: The name of the Tree.
            id: The ID of the tree in the DOM.
            classes: The CSS classes of the tree.
            disabled: Whether the tree is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        # Build up the list of menu options. The caller can pass in either
        # strings or actual MenuOption objects.
        self._options: list[MenuOption[MenuDataType]] = [
            option if isinstance(option, MenuOption) else MenuOption(option)
            for option in options
        ]

        # Now that we know the initial list of options, we need to work out
        # the individual lines that will make up the content of the menu.
        # Each option can be a different height, so we'll render from a list
        # of individual lines, while keeping track of with option they
        # relate to.
        self._lines: list[OptionLineSegments[MenuDataType]] = []
        self._spans: list[OptionLineSpan] = []
        # TODO: Do I need to be telling it what width to deal with? Do I
        # need to be working out all the lines again if I get resized?
        lines_from = self.app.console.render_lines
        line = 0
        for option_index, option in enumerate(self._options):
            lines = [
                OptionLineSegments(option, option_index, line)
                for line in lines_from(option.prompt)
            ]
            self._lines.extend(lines)
            self._spans.append(OptionLineSpan(line, len(lines)))
            line += len(lines)

        # TODO: Decide what the width actually should be in this case. Right
        # now this is just about ensuing the scrolling kicks in.
        self.virtual_size = Size(self.size.width, len(self._lines))

        # Finally, cause the highlighted property to settle down based on
        # the state of the menu in regard to its available options. Be sure
        # to have a look at validate_highlighted.
        self.highlighted = None

    def option(self, index: int) -> MenuOption[MenuDataType]:
        """Get the menu option at the given position in the list of options.

        Args:
            index: The position of the required menu option.

        Returns:
            The menu option at that position.

        Raises:
            IndexError: If there is no menu option at that position.
        """
        return self._options[index]

    def render_line(self, y: int) -> Strip:
        """Render a single line in the menu.

        Args:
            y: The Y offset of the line to render.

        Returns:
            A `Strip` instance for the caller to render.
        """

        # First off, work out the index of line we're working on, based off
        # the current scroll offset plus the line we're being asked to
        # render.
        line = self.scroll_offset.y + y

        # Knowing which line we're going to be drawing, we can now go pull
        # the relevant segments for the line of that particular prompt.
        try:
            strip = Strip(self._lines[line].segments)
        except IndexError:
            # An IndexError means we're drawing in a menu where there's more
            # menu than there are prompts.
            strip = Strip([])

        # If something is highlighted, and the line falls within the span of
        # lines that that highlighted option takes up...
        if self.highlighted is not None and line in self._spans[self.highlighted]:
            # ...paint this as a highlighted option.
            return strip.apply_style(
                self.get_component_rich_style("menu--option-highlighted", partial=True)
            )

        return strip

    def scroll_to_highlight(self) -> None:
        """Ensure that the highlighted option is in view."""
        highlighted = self.highlighted
        assert highlighted is not None
        self.scroll_to_region(
            Region(
                0,
                self._spans[highlighted].first,
                self.size.width,
                self._spans[highlighted].line_count,
            ),
            force=True,
            animate=False,
        )

    def validate_highlighted(self, highlighted: int | None) -> int | None:
        """Validate the `highlighted` property value on access."""
        if not self._options:
            return None
        if highlighted is None or highlighted >= len(self._options):
            return 0
        if highlighted < 0:
            return len(self._options) - 1
        return highlighted

    def _update_for_highlight(self) -> None:
        """React to the highlighted option having changed."""
        highlighted = self.highlighted
        assert highlighted is not None
        self.scroll_to_highlight()
        self.post_message(self.OptionHighlighted(self, highlighted))

    def action_up(self) -> None:
        """Move the highlight up by one option."""
        if self.highlighted is not None:
            self.highlighted -= 1
            self._update_for_highlight()

    def action_down(self) -> None:
        """Move the highlight down by one option."""
        if self.highlighted is not None:
            self.highlighted += 1
            self._update_for_highlight()

    def action_first(self) -> None:
        """Move the highlight to the first option."""
        if self._options:
            self.highlighted = 0
            self._update_for_highlight()

    def action_last(self) -> None:
        """Move the highlight to the last option."""
        if self._options:
            self.highlighted = len(self._options) - 1
            self._update_for_highlight()

    def _page(
        self,
        default: Callable[[], None],
        wrap_around: Callable[[], None],
        direction: Literal[-1, 1],
    ) -> None:
        """Move the highlight by one page.

        Args:
            default: The default action to take if no option is highlighted.
            wrap_around: The action to take if we need to wrap around the ends.
            direction: The direction to head, -1 for up and 1 for down.
        """
        highlighted = self.highlighted
        if highlighted is None:
            # There is no highlight yet so let's go to the default position.
            default()
        else:
            # We want to page roughly by lines, but we're dealing with
            # options that can be a varying number of lines in height. So
            # let's start with the a target line alone.
            target_line = self._spans[highlighted].first + (
                direction * self.scrollable_content_region.height
            )
            try:
                # Now that we've got a target line, let's figure out the
                # index of the target option.
                target_option = self._lines[target_line].option_index
            except IndexError:
                # An index error suggests we've gone out of bounds, let's
                # settle on whatever the call things is a good place to wrap
                # to.
                wrap_around()
            else:
                # Looks like we've figured out the next option to jump to.
                self.highlighted = target_option
                self._update_for_highlight()

    def action_page_up(self) -> None:
        """Move the highlight up one page of options."""
        self._page(self.action_first, self.action_last, -1)

    def action_page_down(self) -> None:
        """Move the highlight down one page of options."""
        self._page(self.action_last, self.action_first, 1)
