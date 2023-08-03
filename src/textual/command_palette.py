"""The Textual command palette."""

from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import Queue, TimeoutError, create_task, wait_for
from typing import (
    Any,
    AsyncIterable,
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
from .app import ComposeResult
from .binding import Binding, BindingType
from .events import Click, Mount
from .reactive import var
from .screen import ModalScreen, Screen
from .widgets import Input, LoadingIndicator, OptionList
from .widgets.option_list import Option

__all__ = [
    "CommandPalette",
    "CommandPaletteCallable",
    "CommandSource",
    "CommandSourceHit",
]


CommandPaletteCallable: TypeAlias = Callable[[], Any]
"""The type of a function that will be called when a command is selected from the command palette."""


class CommandSourceHit(NamedTuple):
    """Holds the details of a single command search hit."""

    match_value: float
    """The match value of the command hit."""

    match_text: Text
    """The [rich.text.Text][`Text`] representation of the hit."""

    command: CommandPaletteCallable
    """The function to call when the command is chosen."""

    command_text: str
    """The command text associated with the hit, as plain text."""

    command_help: str | None = None
    """Optional help text for the command."""


class CommandSource(ABC):
    """Base class for command palette command sources.

    To create a source of commands inherit from this class and implement
    [textual.command_palette.CommandSource.hunt_for][`hunt_for`].
    """

    def __init__(self, screen: Screen) -> None:
        """Initialise the command source.

        Args:
            screen: A reference to the active screen.
        """
        self.__screen = screen

    @property
    def screen(self) -> Screen:
        """The currently-active screen in the application."""
        return self.__screen

    @abstractmethod
    async def hunt_for(self, user_input: str) -> AsyncIterator[CommandSourceHit]:
        """A request to hunt for commands relevant to the given user input.

        Args:
            user_input: The user input to be matched.

        Yields:
            Instances of [CommandSourceHit][`CommandSourceHit`].
        """
        raise NotImplemented


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


class CommandList(OptionList, can_focus=False):
    """The command palette command list."""

    DEFAULT_CSS = """
    CommandList {
        visibility: hidden;
        max-height: 70%;
        border: blank;
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
    CommandInput {
        margin-top: 3;
        border: blank;
    }

    CommandInput:focus {
        border: blank;
    }
    """


class CommandPalette(ModalScreen[CommandPaletteCallable], inherit_css=False):
    """The Textual command palette."""

    DEFAULT_CSS = """
    CommandPalette {
        background: $background 30%;
        align-horizontal: center;
    }

    CommandPalette > * {
        width: 90%;
    }

    CommandPalette LoadingIndicator {
        height: auto;
        width: 90%;
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

    _list_visible: var[bool] = var(False, init=False)
    """Internal reactive to toggle the visibility of the command list."""

    _show_busy: var[bool] = var(False, init=False)
    """Internal reactive to toggle the visibility of the busy indicator."""

    _calling_screen: var[Screen | None] = var(None)
    """A record of the screen that was active when we were called."""

    _sources: set[Type[CommandSource]] = set()
    """The list of command source classes."""

    def __init__(self) -> None:
        super().__init__()
        self._selected_command: CommandSourceHit | None = None
        """The command that was selected by the user."""

    @classmethod
    def register_source(cls, source: Type[CommandSource]) -> None:
        """Register a source of commands for the command palette.

        Args:
            source: The class of the source to register.
        """
        cls._sources.add(source)

    def compose(self) -> ComposeResult:
        """Compose the command palette."""
        yield CommandInput(placeholder="Search...")
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
        # still the head of the stack.
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
        source: AsyncIterable[CommandSourceHit], commands: Queue[CommandSourceHit]
    ) -> None:
        """Consume a source of matching commands, feeding the given command queue.

        Args:
            source: The source to consume.
            commands: The command queue to feed.
        """
        async for hit in source:
            await commands.put(hit)

    async def _hunt_for(self, search_value: str) -> AsyncIterator[CommandSourceHit]:
        """Hunt for a given search value amongst all of the command sources.

        Args:
            search_value: The value to search for.

        Yields:
            The hits made amongst the registered command sources.
        """

        # Set up a queue to stream in the command hits from all the sources.
        commands: Queue[CommandSourceHit] = Queue()

        # Fire up an instance of each command source, inside a task, and
        # have them go start looking for matches.
        searches = [
            create_task(
                self._consume(
                    source(self._calling_screen).hunt_for(search_value), commands
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

    @work(exclusive=True)
    async def _gather_commands(self, search_value: str) -> None:
        """Gather up all of the commands that match the search value.

        Args:
            search_value: The value to search for.
        """
        command_list = self.query_one(CommandList)
        self._show_busy = True
        async for hit in self._hunt_for(search_value):
            prompt = hit.match_text
            if hit.command_help:
                prompt = Table.grid(expand=True)
                prompt.add_column(no_wrap=True)
                prompt.add_row(hit.match_text, style=Style(bold=True))
                prompt.add_row(Align.right(hit.command_help), style=Style(dim=True))
            command_list.add_option(Command(prompt, hit))
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
        command_list = self.query_one(CommandList)
        command_list.clear_options()
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

    @on(Input.Submitted)
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
                # ...so let's get out of here, saying what we want run.
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
