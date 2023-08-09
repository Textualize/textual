"""The Textual command palette."""

from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import Queue, TimeoutError, create_task, wait_for
from functools import total_ordering
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    ClassVar,
    NamedTuple,
    Type,
)

from rich.align import Align
from rich.console import RenderableType
from rich.style import Style
from rich.table import Table
from rich.text import Text
from typing_extensions import TypeAlias

from . import on, work
from ._fuzzy import Matcher
from .binding import Binding, BindingType
from .containers import Horizontal, Vertical
from .events import Click, Mount
from .reactive import var
from .screen import ModalScreen, Screen
from .widget import Widget
from .widgets import Button, Input, LoadingIndicator, OptionList
from .widgets.option_list import Option

if TYPE_CHECKING:
    from .app import App, ComposeResult

__all__ = [
    "CommandMatches",
    "CommandPalette",
    "CommandPaletteCallable",
    "CommandSource",
    "CommandSourceHit",
    "Matcher",
]


CommandPaletteCallable: TypeAlias = Callable[[], Any]
"""The type of a function that will be called when a command is selected from the command palette."""


@total_ordering
class CommandSourceHit(NamedTuple):
    """Holds the details of a single command search hit."""

    match_value: float
    """The match value of the command hit."""

    match_display: RenderableType
    """The [rich.console.RenderableType][renderable] representation of the hit."""

    command: CommandPaletteCallable
    """The function to call when the command is chosen."""

    command_text: str
    """The command text associated with the hit, as plain text."""

    command_help: str | None = None
    """Optional help text for the command."""

    def __lt__(self, other: CommandSourceHit) -> bool:
        return self.match_value < other.match_value

    def __eq__(self, other: CommandSourceHit) -> bool:
        return self.match_value == other.match_value


CommandMatches: TypeAlias = AsyncIterator[CommandSourceHit]
"""Return type for the command source match hunting method."""


class CommandSource(ABC):
    """Base class for command palette command sources.

    To create a source of commands inherit from this class and implement
    [textual.command_palette.CommandSource.hunt_for][`hunt_for`].
    """

    def __init__(self, screen: Screen, match_style: Style | None = None) -> None:
        """Initialise the command source.

        Args:
            screen: A reference to the active screen.
        """
        self.__screen = screen
        self.__match_style = match_style

    @property
    def focused(self) -> Widget | None:
        """The currently-focused widget in the currently-active screen in the application."""
        return self.__screen.focused

    @property
    def screen(self) -> Screen[object]:
        """The currently-active screen in the application."""
        return self.__screen

    @property
    def app(self) -> App[object]:
        """A reference to the application."""
        return self.__screen.app

    @property
    def match_style(self) -> Style | None:
        """The preferred style to use when highlighting matching portions of the `match_display`."""
        return self.__match_style

    def matcher(self, user_input: str, case_sensitive: bool = False) -> Matcher:
        """Create a fuzzy matcher for the given user input.

        Args:
            user_input: The text that the user has input.
            case_sensitive: Should match be case sensitive?

        Returns:
            A fuzzy matcher object for matching against candidate hits.
        """
        return Matcher(
            user_input, match_style=self.match_style, case_sensitive=case_sensitive
        )

    @abstractmethod
    async def hunt_for(self, user_input: str) -> CommandMatches:
        """A request to hunt for commands relevant to the given user input.

        Args:
            user_input: The user input to be matched.

        Yields:
            Instances of [CommandSourceHit][`CommandSourceHit`].
        """
        raise NotImplemented


@total_ordering
class Command(Option):
    """Class that holds a command in the `CommandList`."""

    def __init__(
        self,
        prompt: RenderableType,
        command: CommandSourceHit,
        id: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the option.

        Args:
            prompt: The prompt for the option.
            command: The details of the command associated with the option.
            id: The optional ID for the option.
            disabled: The initial enabled/disabled state. Enabled by default.
        """
        super().__init__(prompt, id, disabled)
        self.command = command
        """The details of the command associated with the option."""

    def __lt__(self, other: Command) -> bool:
        return self.command < other.command

    def __eq__(self, other: Command) -> bool:
        return self.command == other.command


class CommandList(OptionList, can_focus=False):
    """The command palette command list."""

    DEFAULT_CSS = """
    CommandList {
        visibility: hidden;
        border-top: blank;
        border-bottom: hkey $accent;
        border-left: blank;
        border-right: blank;
        height: auto;
        max-height: 70vh;
        background: $panel;
    }

    CommandList:focus {
        border: blank;
    }

    CommandList.--visible {
        visibility: visible;
    }

    CommandList > .option-list--option-highlighted {
        background: $accent;
    }
    """


class CommandInput(Input):
    """The command palette input control."""

    DEFAULT_CSS = """
    CommandInput, CommandInput:focus {
        border: blank;
        width: 1fr;
        background: $panel;
    }
    """


class CommandPalette(ModalScreen[CommandPaletteCallable], inherit_css=False):
    """The Textual command palette."""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "command-palette--help-text",
        "command-palette--highlight",
    }
    """
    | Class | Description |
    | :- | :- |
    | `command-palette--help-text` | Targets the help text of a matched command. |
    | `command-palette--highlight` | Targets the highlights of a matched command. |
    """

    DEFAULT_CSS = """
    CommandPalette {
        background: $background 30%;
        align-horizontal: center;
    }

    CommandPalette > .command-palette--help-text {
        color: $text-muted;
        text-style: italic;
        background: transparent;
    }

    CommandPalette > .command-palette--highlight {
        text-style: reverse;
    }

    CommandPalette > Vertical {
        margin-top: 3;
        width: 90%;
        height: 100%;
        visibility: hidden;
    }

    CommandPalette #--input {
        height: auto;
        visibility: visible;
        border: hkey $accent;
        background: $panel;
    }

    CommandPalette #--input Button {
        min-width: 7;
    }

    CommandPalette #--results {
        overlay: screen;
        height: auto;
    }

    CommandPalette LoadingIndicator {
        height: auto;
        visibility: hidden;
    }

    CommandPalette LoadingIndicator.--visible {
        visibility: visible;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "escape", "Exit the command palette"),
        Binding("down", "cursor_down", show=False),
        Binding("pagedown", "command('page_down')", show=False),
        Binding("pageup", "command('page_up')", show=False),
        Binding("up", "command('cursor_up')", show=False),
        Binding("ctrl+home, shift+home", "command('first')", show=False),
        Binding("ctrl+end, shift+end", "command('last')", show=False),
    ]

    run_on_select: ClassVar[bool] = True
    """A flag to say if a command should be run when selected by the user.

    If `True` then when a user hits `Enter` on a command match in the result
    list, or if they click on one with the mouse, the command will be
    selected and run. If set to `False` the input will be filled with the
    command and then `Enter` should be pressed on the keyboard or the 'go'
    button should be pressed.
    """

    _list_visible: var[bool] = var(False, init=False)
    """Internal reactive to toggle the visibility of the command list."""

    _show_busy: var[bool] = var(False, init=False)
    """Internal reactive to toggle the visibility of the busy indicator."""

    _calling_screen: var[Screen | None] = var(None)
    """A record of the screen that was active when we were called."""

    _sources: ClassVar[set[Type[CommandSource]]] = set()
    """The list of command source classes."""

    def __init__(self) -> None:
        """Initialise the command palette."""
        super().__init__()
        self._selected_command: CommandSourceHit | None = None
        """The command that was selected by the user."""

    @classmethod
    def register_source(cls, source: Type[CommandSource]) -> None:
        """Register a source of commands for the command palette.

        Args:
            source: The class of the source to register.

        If the same source is registered more than once, subsequent
        registrations are ignored.
        """
        cls._sources.add(source)

    def compose(self) -> ComposeResult:
        """Compose the command palette.

        Returns:
            The content of the screen.
        """
        with Vertical():
            with Horizontal(id="--input"):
                yield CommandInput(placeholder="Search...")
                if not self.run_on_select:
                    yield Button("\u25b6")
            with Vertical(id="--results"):
                yield CommandList()
                yield LoadingIndicator()

    def _on_click(self, event: Click) -> None:
        """Handle the click event.

        Args:
            event: The click event.

        This method is used to allow clicking on the 'background' as a
        method of dismissing the palette.
        """
        if self.get_widget_at(event.screen_x, event.screen_y)[0] is self:
            self.dismiss()

    def _on_mount(self, _: Mount) -> None:
        """Capture the calling screen."""
        # NOTE: As of the time of writing, during the mount event of a
        # pushed screen, the screen that was in play during the push is
        # still at the head of the stack. We save it so we can pass it on to
        # the command providers.
        self._calling_screen = self.app.screen_stack[0]

    def _watch__list_visible(self) -> None:
        """React to the list visible flag being toggled."""
        self.query_one(CommandList).set_class(self._list_visible, "--visible")
        if not self._list_visible:
            self._show_busy = False

    async def _watch__show_busy(self) -> None:
        """React to the show busy flag being toggled.

        This watcher adds or removes a busy indication depending on the
        flag's state.
        """
        self.query_one(LoadingIndicator).set_class(self._show_busy, "--visible")

    @staticmethod
    async def _consume(
        source: CommandMatches, commands: Queue[CommandSourceHit]
    ) -> None:
        """Consume a source of matching commands, feeding the given command queue.

        Args:
            source: The source to consume.
            commands: The command queue to feed.
        """
        async for hit in source:
            await commands.put(hit)

    async def _hunt_for(self, search_value: str) -> CommandMatches:
        """Hunt for a given search value amongst all of the command sources.

        Args:
            search_value: The value to search for.

        Yields:
            The hits made amongst the registered command sources.
        """

        # Get the style for highlighted parts of a hit match.
        match_style = self._sans_background(
            self.get_component_rich_style("command-palette--highlight")
        )

        # Set up a queue to stream in the command hits from all the sources.
        commands: Queue[CommandSourceHit] = Queue()

        # Fire up an instance of each command source, inside a task, and
        # have them go start looking for matches.
        searches = [
            create_task(
                self._consume(
                    source(self._calling_screen, match_style).hunt_for(search_value),
                    commands,
                )
            )
            for source in self._sources
        ]

        # Now, while there's some task running...
        while any(not search.done() for search in searches):
            try:
                # ...briefly wait for something on the stack. If we get
                # something yield it up to our caller.
                yield await wait_for(commands.get(), 0.1)
            except TimeoutError:
                # A timeout is fine. We're just going to go back round again
                # and see if anything else has turned up.
                pass
            else:
                # There was no timeout, which means that we managed to yield
                # up that command; we're done with it so let the queue know.
                commands.task_done()

        # If all the sources are pretty fast it could be that we've reached
        # this point but the queue isn't empty yet. So here we flush the
        # queue of anything left. Note though that rather than busy-spin the
        # queue and just pull items and yield them, we keep using the
        # await/wait_for so we don't block until we're done. Not doing this
        # makes typing into the input *very* choppy when you have very fast
        # sources.
        while not commands.empty():
            try:
                yield await wait_for(commands.get(), 0.1)
            except TimeoutError:
                pass

    @staticmethod
    def _sans_background(style: Style) -> Style:
        """Returns the given style minus the background color.

        Args:
            style: The style to remove the color from.

        Returns:
            The given style, minus its background.
        """
        # Here we're pulling out all of the styles *minus* the background.
        # This should probably turn into a utility method on Style
        # eventually. The reason for this is we want the developer to be
        # able to style the help text with a component class, but we want
        # the background to always be the background at any given moment in
        # the context of an OptionList. At the moment this act of copying
        # sans bgcolor seems to be the only way to achieve this.
        return Style(
            blink2=style.blink2,
            blink=style.blink,
            bold=style.bold,
            color=style.color,
            conceal=style.conceal,
            dim=style.dim,
            encircle=style.encircle,
            frame=style.frame,
            italic=style.italic,
            link=style.link,
            overline=style.overline,
            reverse=style.reverse,
            strike=style.strike,
            underline2=style.underline2,
            underline=style.underline,
        )

    def _refresh_command_list(
        self, command_list: CommandList, commands: list[Command]
    ) -> None:
        """Refresh the command list.

        Args:
            command_list: The widget that shows the list of commands.
            commands: The commands to show in the widget.
        """
        # For the moment, this is a fairly naive approach to populating the
        # command list with a sorted list of commands. Every time we add a
        # new one we're nuking the list of options and populating them
        # again. If this turns out to not be a great approach, we may try
        # and get a lot smarter with this (ideally OptionList will grow a
        # method to sort its content in an efficient way; but for now we'll
        # go with "worse is better" wisdom).

        # First off, we sort the commands, best to worst.
        sorted_commands = sorted(commands, reverse=True)

        # If the newly-appended command is still at the end after we've
        # sorted...
        if sorted_commands[-1] == commands[-1]:
            # ...we can just add the command to the option list without
            # further fuss.
            command_list.add_option(commands[-1])
        else:
            # Nope, it's slotting in somewhere other than at the end, so
            # we'll remember where we were, clear the commands in the list,
            # add the sorted set back and apply the highlight again. Note
            # that remembering where we were is remembering the option we
            # were on, not the index.
            highlighted = (
                command_list.get_option_at_index(command_list.highlighted)
                if command_list.highlighted is not None
                else None
            )
            command_list.clear_options().add_options(sorted_commands)
            if highlighted is not None:
                command_list.highlighted = command_list.get_option_index(highlighted.id)

    @work(exclusive=True)
    async def _gather_commands(self, search_value: str) -> None:
        """Gather up all of the commands that match the search value.

        Args:
            search_value: The value to search for.
        """
        help_style = self._sans_background(
            self.get_component_rich_style("command-palette--help-text")
        )
        gathered_commands: list[Command] = []
        command_list = self.query_one(CommandList)
        command_id = 0
        self._show_busy = True
        async for hit in self._hunt_for(search_value):
            prompt = hit.match_display
            if hit.command_help:
                # Because there's some help for the command, we switch to a
                # Rich table so we can individually align a couple of rows;
                # the command will be left-aligned, the help however will be
                # right-aligned.
                prompt = Table.grid(expand=True)
                prompt.add_column(no_wrap=True)
                prompt.add_row(hit.match_display)
                prompt.add_row(Align.right(Text(hit.command_help, style=help_style)))
            gathered_commands.append(Command(prompt, hit, id=str(command_id)))
            self._refresh_command_list(command_list, gathered_commands)
            command_id += 1
        self._show_busy = False
        if command_list.option_count == 0:
            command_list.add_option(
                Option(Align.center(Text("No matches found")), disabled=True)
            )

    @on(Input.Changed)
    def _input(self, event: Input.Changed) -> None:
        """React to input in the command palette.

        Args:
            event: The input event.
        """
        search_value = event.value.strip()
        self._list_visible = bool(search_value)
        self.query_one(CommandList).clear_options()
        if search_value:
            self._gather_commands(search_value)

    @on(OptionList.OptionSelected)
    def _select_command(self, event: OptionList.OptionSelected) -> None:
        """React to a command being selected from the dropdown.

        Args:
            event: The option selection event.
        """
        event.stop()
        input = self.query_one(CommandInput)
        with self.prevent(Input.Changed):
            assert isinstance(event.option, Command)
            input.value = str(event.option.command.command_text)
            self._selected_command = event.option.command
        input.action_end()
        self._list_visible = False
        if self.run_on_select:
            self._select_or_command()

    @on(Input.Submitted)
    @on(Button.Pressed)
    def _select_or_command(self) -> None:
        """Depending on context, select or execute a command."""
        # If the list is visible, that means we're in "pick a command" mode
        # still and so we should bounce this command off to the command
        # list.
        if self._list_visible:
            self._action_command("select")
        else:
            # The list isn't visible, which means that if we have a
            # command...
            if self._selected_command is not None:
                # ...we should run return it to the parent screen and let it
                # decide what to do with it (hopefully it'll run it).
                self.dismiss(self._selected_command.command)

    def _action_escape(self) -> None:
        """Handle a request to escape out of the command palette."""
        if self._list_visible:
            self._list_visible = False
        else:
            self.app.pop_screen()

    def _action_command(self, action: str) -> None:
        """Pass an action on to the `CommandList`.

        Args:
            action: The action to pass on to the `CommandList`.
        """
        try:
            command_action = getattr(self.query_one(CommandList), f"action_{action}")
        except AttributeError:
            return
        command_action()

    def _action_cursor_down(self) -> None:
        """Handle the cursor down action.

        This allows the cursor down key to either open the command list, if
        it's closed but has options, or if it's open with options just
        cursor through them.
        """
        if self.query_one(CommandList).option_count and not self._list_visible:
            self._list_visible = True
            self.query_one(CommandList).highlighted = 0
        else:
            self._action_command("cursor_down")
