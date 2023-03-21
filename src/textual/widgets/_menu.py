"""Provides the core of a classic vertical bounce-bar menu."""

from __future__ import annotations

from typing import Callable, ClassVar, NamedTuple

from rich.console import RenderableType
from rich.repr import Result
from rich.rule import Rule
from rich.segment import Segment
from typing_extensions import Literal, Self

from ..binding import Binding, BindingType
from ..geometry import Region, Size
from ..message import Message
from ..reactive import reactive
from ..scroll_view import ScrollView
from ..strip import Strip


class DuplicateID(Exception):
    """Exception raised if a duplicate ID is used."""


class MenuOption(NamedTuple):
    """Class that holds the details of an individual menu option."""

    prompt: RenderableType
    """The prompt for the menu option."""
    id: str | None = None
    """An optional ID to associate with the menu option."""
    disabled: bool = False
    """Is the menu option disabled?"""


class MenuSeparator:
    """Class that denotes that a particular option is really a menu separator."""


class Line(NamedTuple):
    """Class that holds a list of segments for the line of a menu option."""

    segments: list[Segment]
    """The list of segments that make up the line."""

    option_index: int | None = None
    """The index of the [MenuOption][textual.widgets.menu.MenuOption] that this line is related to.

    If the line isn't related to a menu option this will be `None`.
    """


class OptionLineSpan(NamedTuple):
    """Class that holds the line span information for a menu option.

    A [MenuOption][textual.widgets.menu.MenuOption] can have a prompt that
    spans multiple lines. Also, there's no requirement that every option in
    a menu has the same span information. So this structure is used to track
    the line that an option starts on, and how many lines it contains.
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


class Menu(ScrollView, can_focus=True):
    """A vertical bounce-bar menu."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("up", "up", "Up", show=False),
        Binding("down", "down", "Down", show=False),
        Binding("home", "first", "First", show=False),
        Binding("end", "last", "Last", show=False),
        Binding("page_up", "page_up", "Page Up", show=False),
        Binding("page_down", "page_down", "Page Down", show=False),
        Binding("enter", "select", "Select", show=False),
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
    | enter | Select the current menu option. |
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "menu--option-highlighted",
        "menu--option-highlighted-disabled",
        "menu--option-hover",
        "menu--option-disabled",
        "menu--separator",
    }
    """
    | Class | Description |
    | :- | :- |
    | `menu--option-highlighted` | Target the highlighted menu option. |
    | `menu--separator` | Target the menu separators. |
    """

    DEFAULT_CSS = """
    Menu {
        background: $panel-lighten-1;
        overflow: hidden;
        color: $text;
    }

    Menu > .menu--separator {
        color: $text-muted;
    }

    Menu > .menu--option-highlighted {
        background: $accent 50%;
        color: $text;
        text-style: bold;
    }

    Menu:focus > .menu--option-highlighted {
        background: $accent;
    }

    Menu > .menu--option-disabled {
        color: $text-disabled;
    }

    Menu > .menu--option-highlighted-disabled {
        color: $text-disabled;
        background: $accent 30%;
    }

    Menu:focus > .menu--option-highlighted-disabled {
        background: $accent 40%;
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

    class OptionMessage(Message):
        """Base class for all menu option messages."""

        def __init__(self, menu: Menu, index: int) -> None:
            """Initialise the option message.

            Args:
                menu: The menu that owns the option.
                option: The option that the messages relates to.
            """
            super().__init__()
            self.menu: Menu = menu
            """The menu that sent the message."""
            self.option: MenuOption = menu.get_option_at_index(index)
            """The highlighted option."""
            self.option_id: str | None = self.option.id
            """The ID of the option that the message relates to."""
            self.option_index: int = index
            """The index of the option that the message relates to."""

        def __rich_repr__(self) -> Result:
            yield "menu", self.menu
            yield "option", self.option
            yield "option_id", self.option_id
            yield "option_index", self.option_index

    class OptionHighlighted(OptionMessage):
        """Message sent when an option is highlighted.

        Can be handled using `on_menu_option_highlighted` in a subclass of
        `Menu` or in a parent node in the DOM.
        """

    class OptionSelected(OptionMessage):
        """Message sent when an option is selected.

        Can be handled using `on_menu_option_selected` in a subclass of
        `Menu` or in a parent node in the DOM.
        """

    def __init__(
        self,
        *options: MenuOption | MenuSeparator | RenderableType,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the menu.

        Args:
            *options: The options for the menu.
            name: The name of the Menu.
            id: The ID of the menu in the DOM.
            classes: The CSS classes of the menu.
            disabled: Whether the menu is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self._contents: list[MenuOption | MenuSeparator] = [
            self._make_content(option) for option in options
        ]
        """A list of the content of the menu.

        This is *every* that makes up the content of the menu; this includes
        both the prompts *and* the separators (and any other decoration we
        could end up adding -- although I don't anticipate anything else at
        the moment; but padding around separators could be a thing,
        perhaps).
        """

        self._options: list[MenuOption] = [
            content for content in self._contents if isinstance(content, MenuOption)
        ]
        """A list of the options within the menu.

        This is a list of references to just the options alone, ignoring the
        separators and potentially any other line-oriented menu content that
        isn't an option.
        """

        self._option_ids: dict[str, int] = {}
        """A dictionary of menu IDs and the option indexes they relate to."""

        self._lines: list[Line] = []
        """A list of all of the individual lines that make up the menu.

        Note that the size of this list will at least the same as the number
        of options, and actually greater if any prompt of any option is
        multiple lines.
        """

        self._spans: list[OptionLineSpan] = []
        """A list of the locations and sizes of all options in the menu.

        This will be the same size as the number of prompts; each entry in
        the list contains the line offset of the start of the prompt, and
        the count of the lines in the prompt.
        """

        # Initial calculation of the content tracking.
        self._refresh_content_tracking()

        # Finally, cause the highlighted property to settle down based on
        # the state of the menu in regard to its available options. Be sure
        # to have a look at validate_highlighted.
        self.highlighted = None

    def _make_content(
        self, content: MenuOption | MenuSeparator | RenderableType
    ) -> MenuOption | MenuSeparator:
        """Convert a single item of content for the menu into a menu content type.

        Args:
            content: The content to turn into a full menu type.

        Returns:
            The content, usable in the menu.
        """
        return (
            content
            if isinstance(content, (MenuOption, MenuSeparator))
            else MenuOption(content)
        )

    def _clear_content_tracking(self) -> None:
        """Clear down the content tracking information."""
        self._lines.clear()
        self._spans.clear()
        self._option_ids.clear()

    def _refresh_content_tracking(self) -> None:
        """Refresh the various forms of menu content tracking."""

        self._clear_content_tracking()

        # TODO: Do I need to be telling it what width to deal with? Do I
        # need to be working out all the lines again if I get resized?
        lines_from = self.app.console.render_lines

        # Create a rule that can be used as a separator.
        separator = lines_from(Rule(style=""))[0]

        # Set up for doing less property access work inside the loop.
        spans = self._spans
        option_ids = self._option_ids
        lines = self._lines

        # Work through each item that makes up the content of the menu,
        # break out the individual lines that will be used to draw it, and
        # also set up the tracking of the actual menu options.
        line = 0
        option = 0
        for content in self._contents:
            if isinstance(content, MenuOption):
                # The content is a menu option, so render out the prompt and
                # work out the lines needed to show it.
                new_lines = [
                    Line(prompt_line, option)
                    for prompt_line in lines_from(content.prompt)
                ]
                # Record the span information for the option.
                spans.append(OptionLineSpan(line, len(new_lines)))
                if content.id is not None:
                    # The option has an ID set, create a mapping from that
                    # ID to the option so we can use it later.
                    if content.id in option_ids:
                        raise DuplicateID(
                            f"The menu already has an option with id '{content.id}'"
                        )
                    option_ids[content.id] = option
                option += 1
            else:
                # The content isn't a menu option, so it must be a separator
                # (if there were to be other non-option content for a menu
                # it's in this if/else where we'd process it).
                new_lines = [Line(separator)]
            lines.extend(new_lines)
            line += len(new_lines)

        # TODO: Decide what the width actually should be in this case. Right
        # now this is just about ensuing the scrolling kicks in.
        self.virtual_size = Size(self.size.width, len(self._lines))

    def add(self, option: MenuOption | MenuSeparator | RenderableType) -> Self:
        """Add a new option to the end of the menu.

        Args:
            option: The option to add.

        Returns:
            The menu.
        """
        # Turn any renderable into actual menu content.
        content = self._make_content(option)
        self._contents.append(content)
        # If the content is a genuine menu option, add it to the list of options.
        if isinstance(content, MenuOption):
            self._options.append(content)
        self._refresh_content_tracking()
        self.refresh()
        return self

    def clear(self) -> Self:
        """Clear the content of the menu.

        Returns:
            The menu.
        """
        self._contents.clear()
        self._options.clear()
        self._refresh_content_tracking()
        self.highlighted = None
        self.virtual_size = Size(self.size.width, 0)
        self.refresh()
        return self

    def _set_option_disabled(self, index: int, disabled: bool) -> Self:
        """Set the disabled state of a menu option.

        Args:
            index: The index of the option to set the disabled state of.
            disabled: The disabled state to set.

        Returns:
            The menu.
        """
        old_prompt, old_id, *_ = self._options[index]
        self._options[index] = MenuOption(old_prompt, old_id, disabled)
        # TODO: Refresh only if the affected option is visible.
        self.refresh()
        return self

    def enable_option_at_index(self, index: int) -> Self:
        """Enable the menu option at the given index.

        Returns:
            The menu.

        Raises:
            IndexError: If there is no menu option with the given index.
        """
        return self._set_option_disabled(index, False)

    def disable_option_at_index(self, index: int) -> Self:
        """Disable the menu option at the given index.

        Returns:
            The menu.

        Raises:
            IndexError: If there is no menu option with the given index.
        """
        return self._set_option_disabled(index, True)

    def enable_option(self, option_id: str) -> Self:
        """Enable the menu option with the given ID.

        Args:
            option_id: The ID of the option to enable.

        Returns:
            The menu.

        Raises:
            KeyError: If no option in the menu has the given ID.
        """
        return self.enable_option_at_index(self._option_ids[option_id])

    def disable_option(self, option_id: str) -> Self:
        """Disable the menu option with the given ID.

        Args:
            option_id: The ID of the option to disable.

        Returns:
            The menu.

        Raises:
            KeyError: If no option in the menu has the given ID.
        """
        return self.disable_option_at_index(self._option_ids[option_id])

    @property
    def option_count(self) -> int:
        """The count of options in the menu."""
        return len(self._options)

    def get_option_at_index(self, index: int) -> MenuOption:
        """Get the menu option at the given index.

        Args:
            index: The index of the option to get.

        Returns:
            The option at that index.

        Raises:
            IndexError: If there is no option with the index.
        """
        return self._options[index]

    def get_option(self, option_id: str) -> MenuOption:
        """Get the menu option with the given ID.

        Args:
            index: The ID of the option to get.

        Returns:
            The option at with the ID.

        Raises:
            KeyError: If no option in the menu has the given ID.
        """
        return self.get_option_at_index(self._option_ids[option_id])

    def render_line(self, y: int) -> Strip:
        """Render a single line in the menu.

        Args:
            y: The Y offset of the line to render.

        Returns:
            A `Strip` instance for the caller to render.
        """

        # First off, work out which line we're working on, based off the
        # current scroll offset plus the line we're being asked to render.
        line_number = self.scroll_offset.y + y
        try:
            line = self._lines[line_number]
        except IndexError:
            # An IndexError means we're drawing in a menu where there's more
            # menu than there are prompts.
            return Strip([])

        # Knowing which line we're going to be drawing, we can now go pull
        # the relevant segments for the line of that particular prompt.
        strip = Strip(line.segments)

        # If the line we're looking at isn't associated with a menu option,
        # it will be a separator, so let's exit early with that.
        if line.option_index is None:
            return strip.apply_style(self.get_component_rich_style("menu--separator"))

        # If the option we're drawing is disabled, exit with an option style.
        if self._options[line.option_index].disabled:
            if line.option_index == self.highlighted:
                return strip.apply_style(
                    self.get_component_rich_style("menu--option-highlighted-disabled")
                )
            return strip.apply_style(
                self.get_component_rich_style("menu--option-disabled")
            )

        # If something is highlighted, and the line falls within the span of
        # lines that that highlighted option takes up...
        if (
            self.highlighted is not None
            and line_number in self._spans[self.highlighted]
        ):
            # ...paint this as a highlighted option.
            return strip.apply_style(
                self.get_component_rich_style("menu--option-highlighted")
            )

        # It's a normal option line.
        return strip.apply_style(self.rich_style)

    def scroll_to_highlight(self) -> None:
        """Ensure that the highlighted option is in view."""
        highlighted = self.highlighted
        assert highlighted is not None
        span = self._spans[highlighted]
        self.scroll_to_region(
            Region(0, span.first, self.size.width, span.line_count),
            force=True,
            animate=False,  # https://github.com/Textualize/textual/issues/2077
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
        if not self._options[highlighted].disabled:
            self.post_message(self.OptionHighlighted(self, highlighted))

    def action_up(self) -> None:
        """Move the highlight up by one option."""
        if self.highlighted is not None:
            self.highlighted -= 1
            self._update_for_highlight()
        elif self._options:
            self.action_first()

    def action_down(self) -> None:
        """Move the highlight down by one option."""
        if self.highlighted is not None:
            self.highlighted += 1
            self._update_for_highlight()
        elif self._options:
            self.action_first()

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

    def action_select(self) -> None:
        """Select the currently-highlighted menu option.

        If no option is selected, then nothing happens. If an option is
        selected, a [Menu.OptionSelected][textual.widgets.Menu.OptionSelected]
        message will be posted.
        """
        highlighted = self.highlighted
        if highlighted is not None and not self._options[highlighted].disabled:
            self.post_message(self.OptionSelected(self, highlighted))
