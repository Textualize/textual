"""A command palette command source for Textual system commands.

This is a simple command source that makes the most obvious application
actions available via the [command palette][textual.command_palette.CommandPalette].
"""

from __future__ import annotations

from typing import Callable, NamedTuple

from .command_palette import CommandMatches, CommandSource, CommandSourceHit


class SystemCommand(NamedTuple):
    """Holds the details of a system-wide command."""

    name: str
    """The name for the command; the string that will be matched."""
    run: Callable[[], None]
    """The code to run when the command is selected."""
    help: str
    """Help text for the command."""


class SystemCommandSource(CommandSource):
    """A [source][textual.command_palette.CommandSource] of command palette commands that run app-wide tasks."""

    async def hunt_for(self, user_input: str) -> CommandMatches:
        """Handle a request to hunt for system commands that match the user input.

        Args:
            user_input: The user input to be matched.

        Yields:
            Command source hits for use in the command palette.
        """
        # We're going to use Textual's builtin fuzzy matcher to find
        # matching commands.
        matcher = self.matcher(user_input)

        # Loop over all applicable commands, find those that match and offer
        # them up to the command palette.
        for command in (
            SystemCommand(
                "Toggle light/dark mode",
                self.run(self.app.action_toggle_dark),
                "Toggle the application between light and dark mode",
            ),
            SystemCommand(
                "Save a screenshot",
                self.run(self.app.action_screenshot),
                "Save a SVG file to storage that contains the contents of the current screen",
            ),
            SystemCommand(
                "Quit the application",
                self.run(self.app.action_quit),
                "Quit the application as soon as possible",
            ),
            SystemCommand(
                "Ring the bell",
                self.run(self.app.action_bell),
                "Ring the terminal's 'bell'",
            ),
        ):
            match = matcher.match(command.name)
            if match > 0:
                yield CommandSourceHit(
                    match,
                    matcher.highlight(command.name),
                    command.run,
                    command.name,
                    command.help,
                )
