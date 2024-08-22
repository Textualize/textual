"""

This module contains `SystemCommands`, a command palette command provider for Textual system commands.

This is a simple command provider that makes the most obvious application
actions available via the [command palette][textual.command.CommandPalette].

!!! note

    The App base class installs this automatically.

"""

from __future__ import annotations

from typing import Iterable

from .command import DiscoveryHit, Hit, Hits, Provider
from .types import IgnoreReturnCallbackType


class SystemCommands(Provider):
    """A [source][textual.command.Provider] of command palette commands that run app-wide tasks.

    Used by default in [`App.COMMANDS`][textual.app.App.COMMANDS].
    """

    @property
    def _system_commands(self) -> Iterable[tuple[str, IgnoreReturnCallbackType, str]]:
        """The system commands to reveal to the command palette."""
        if self.app.dark:
            yield (
                "Light mode",
                self.app.action_toggle_dark,
                "Switch to a light background",
            )
        else:
            yield (
                "Dark mode",
                self.app.action_toggle_dark,
                "Switch to a dark background",
            )

        yield (
            "Quit the application",
            self.app.action_quit,
            "Quit the application as soon as possible",
        )

        if self.screen.query("HelpPanel"):
            yield (
                "Hide keys and help panel",
                self.app.action_hide_help_panel,
                "Hide the keys and widget help panel",
            )
        else:
            yield (
                "Show keys and help panel",
                self.app.action_show_help_panel,
                "Show help for the focused widget and a summary of available keys",
            )

    async def discover(self) -> Hits:
        """Handle a request for the discovery commands for this provider.

        Yields:
            Commands that can be discovered.
        """
        commands = sorted(self._system_commands, key=lambda command: command[0])
        for name, runnable, help_text in commands:
            yield DiscoveryHit(
                name,
                runnable,
                help=help_text,
            )

    async def search(self, query: str) -> Hits:
        """Handle a request to search for system commands that match the query.

        Args:
            query: The user input to be matched.

        Yields:
            Command hits for use in the command palette.
        """
        # We're going to use Textual's builtin fuzzy matcher to find
        # matching commands.
        matcher = self.matcher(query)

        # Loop over all applicable commands, find those that match and offer
        # them up to the command palette.
        for name, runnable, help_text in self._system_commands:
            if (match := matcher.match(name)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(name),
                    runnable,
                    help=help_text,
                )
