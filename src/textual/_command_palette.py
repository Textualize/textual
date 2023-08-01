"""The Textual command palette."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, NamedTuple

from rich.align import Align
from rich.console import RenderableType
from rich.style import Style
from rich.table import Table
from rich.text import Text

from . import on, work
from ._fuzzy import Matcher
from .app import ComposeResult
from .binding import Binding
from .css.query import NoMatches
from .reactive import var
from .screen import ModalScreen
from .widgets import Input, LoadingIndicator, OptionList
from .widgets.option_list import Option


class CommandSourceHit(NamedTuple):
    """Holds the details of a single command search hit."""

    match_value: float
    """The match value of the command hit."""

    match_text: Text
    """The [rich.text.Text][`Text`] representation of the hit."""

    command_text: str
    """The command text associated with the hit, as plain text."""

    command_help: str | None = None
    """Optional help text for the command."""


class CommandSource(ABC):
    """Base class for command palette command sources.

    To create a source of commands inherit from this class and implement
    [CommandSource.hunt_for][`hunt_for`].
    """

    @abstractmethod
    async def hunt_for(self, user_input: str) -> AsyncIterator[CommandSourceHit]:
        """A request to hunt for commands relevant to the given user input.

        Args:
            user_input: The user input to be matched.

        Yields:
            Instances of [CommandSourceHit][`CommandSourceHut`].
        """
        raise NotImplemented


class TotallyFakeCommandSource(CommandSource):
    """Really, this isn't going to be the UI. Not even close."""

    DATA = """\
A bird in the hand is worth two in the bush.
A chain is only as strong as its weakest link.
A fool and his money are soon parted.
A man's reach should exceed his grasp.
A picture is worth a thousand words.
A stitch in time saves nine.
Absence makes the heart grow fonder.
Actions speak louder than words.
Although never is often better than *right* now.
Although practicality beats purity.
Although that way may not be obvious at first unless you're Dutch.
Anything is possible.
Be grateful for what you have.
Be kind to yourself and to others.
Be open to new experiences.
Be the change you want to see in the world.
Beautiful is better than ugly.
Believe in yourself.
Better late than never.
Complex is better than complicated.
Curiosity killed the cat.
Don't judge a book by its cover.
Don't put all your eggs in one basket.
Enjoy the ride.
Errors should never pass silently.
Explicit is better than implicit.
Flat is better than nested.
Follow your dreams.
Follow your heart.
Forgive yourself and others.
Fortune favors the bold.
He who hesitates is lost.
If the implementation is easy to explain, it may be a good idea.
If the implementation is hard to explain, it's a bad idea.
If wishes were horses, beggars would ride.
If you can't beat them, join them.
If you can't do it right, don't do it at all.
If you don't like something, change it. If you can't change it, change your attitude.
If you want something you've never had, you have to do something you've never done.
In the face of ambiguity, refuse the temptation to guess.
It's better to have loved and lost than to have never loved at all.
It's not over until the fat lady sings.
Knowledge is power.
Let go of the past and focus on the present.
Life is a journey, not a destination.
Live each day to the fullest.
Live your dreams.
Look before you leap.
Make a difference.
Make the most of every moment.
Namespaces are one honking great idea -- let's do more of those!
Never give up.
Never say never.
No man is an island.
No pain, no gain.
Now is better than never.
One for all and all for one.
One man's trash is another man's treasure.
Readability counts.
Silence is golden.
Simple is better than complex.
Sparse is better than dense.
Special cases aren't special enough to break the rules.
The answer is always in the last place you look.
The best defense is a good offense.
The best is yet to come.
The best way to predict the future is to create it.
The early bird gets the worm.
The exception proves the rule.
The future belongs to those who believe in the beauty of their dreams.
The future is not an inheritance, it is an opportunity and an obligation.
The grass is always greener on the other side.
The journey is the destination.
The journey of a thousand miles begins with a single step.
The more things change, the more they stay the same.
The only person you are destined to become is the person you decide to be.
The only way to do great work is to love what you do.
The past is a foreign country, they do things differently there.
The pen is mightier than the sword.
The road to hell is paved with good intentions.
The sky is the limit.
The squeaky wheel gets the grease.
The whole is greater than the sum of its parts.
The world is a beautiful place, don't be afraid to explore it.
The world is your oyster.
There is always something to be grateful for.
There should be one-- and preferably only one --obvious way to do it.
There's no such thing as a free lunch.
Too many cooks spoil the broth.
United we stand, divided we fall.
Unless explicitly silenced.
We are all in this together.
What doesn't kill you makes you stronger.
When in doubt, consult a chicken.
You are the master of your own destiny.
You can't have your cake and eat it too.
You can't teach an old dog new tricks.
    """.strip().splitlines()

    async def hunt_for(self, user_input: str) -> AsyncIterator[CommandSourceHit]:
        """A request to hunt for commands relevant to the given user input.

        Args:
            user_input: The user input to be matched.
        """
        from asyncio import sleep
        from random import random

        matcher = Matcher(user_input)
        for candidate in self.DATA:
            await sleep(random() / 10)
            if matcher.match(candidate):
                yield CommandSourceHit(
                    matcher.match(candidate),
                    matcher.highlight(candidate),
                    candidate,
                    "This is some help; this could be more interesting really",
                )


class Command(Option):
    """Class that holds a command in the `CommandList`."""

    def __init__(
        self,
        prompt: RenderableType,
        command_text: str,
        id: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the option.

        Args:
            prompt: The prompt for the option.
            command_text: The text of the command.
            id: The optional ID for the option.
            disabled: The initial enabled/disabled state. Enabled by default.
        """
        super().__init__(prompt, id, disabled)
        self.command_text = command_text


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


class CommandPalette(ModalScreen[None], inherit_css=False):
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
    }
    """

    BINDINGS = [
        Binding("escape", "escape", "Exit the command palette"),
        Binding("down", "cursor_down", show=False),
        Binding("pagedown", "command('page_down')", show=False),
        Binding("pageup", "command('page_up')", show=False),
        Binding("up", "command('cursor_up')", show=False),
        Binding("enter", "command('select'),", show=False, priority=True),
    ]

    placeholder: var[str] = var("Textual spotlight search", init=False)
    """The placeholder text for the command palette input."""

    _list_visible: var[bool] = var(False, init=False)
    """Internal reactive to toggle the visibility of the command list."""

    _show_busy: var[bool] = var(False, init=False)
    """Internal reactive to toggle the visibility of the busy indicator."""

    def compose(self) -> ComposeResult:
        """Compose the command palette."""
        yield CommandInput(placeholder=self.placeholder)
        yield CommandList()

    def _watch_placeholder(self) -> None:
        """Pass the new placeholder text down to the `CommandInput`."""
        self.query_one(CommandInput).placeholder = self.placeholder

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
        # First off, figure out if there's an indicator in the DOM.
        try:
            indicator = self.query_one(LoadingIndicator)
        except NoMatches:
            indicator = None
        # Now react to the flag, using the above knowledge to decide what to do.
        if self._show_busy and indicator is None:
            await self.mount(LoadingIndicator(), after=self.query_one(CommandList))
        elif indicator is not None:
            await indicator.remove()

    @work(exclusive=True)
    async def _gather_commands(self, search_value: str) -> None:
        """Gather up all of the commands that match the search value.

        Args:
            search_value: The value to search for.
        """
        command_list = self.query_one(CommandList)
        self._show_busy = True
        async for hit in TotallyFakeCommandSource().hunt_for(search_value):
            prompt = hit.match_text
            if hit.command_help:
                prompt = Table.grid(expand=True)
                prompt.add_column(no_wrap=True)
                prompt.add_row(hit.match_text, style=Style(bold=True))
                prompt.add_row(Align.right(hit.command_help), style=Style(dim=True))
            command_list.add_option(Command(prompt, hit.command_text))
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
            input.value = str(event.option.command_text)
        input.action_end()
        self._list_visible = False

    def _action_escape(self) -> None:
        """Handle a request to escape out of the command palette."""
        if self._list_visible:
            self._list_visible = False
        else:
            self.dismiss()

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
