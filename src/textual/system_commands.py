"""

This module contains `SystemCommands`, a command palette command provider for Textual system commands.

This is a simple command provider that makes the most obvious application
actions available via the [command palette][textual.command.CommandPalette].

!!! note

    The App base class installs this automatically.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .command import DiscoveryHit, Hit, Hits, Provider

if TYPE_CHECKING:
    from .app import SystemCommandsResult


class SystemCommandsProvider(Provider):
    """A [source][textual.command.Provider] of command palette commands that run app-wide tasks.

    Used by default in [`App.COMMANDS`][textual.app.App.COMMANDS].
    """

    @property
    def _system_commands(self) -> SystemCommandsResult:
        """The system commands to reveal to the command palette."""
        yield from self.app.get_system_commands(self.screen)

    async def discover(self) -> Hits:
        """Handle a request for the discovery commands for this provider.

        Yields:
            Commands that can be discovered.
        """
        commands = sorted(self._system_commands, key=lambda command: command[0])
        for name, help_text, callback, discover in commands:
            if discover:
                yield DiscoveryHit(
                    name,
                    callback,
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
        for name, help_text, callback, *_ in self._system_commands:
            if (match := matcher.match(name)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(name),
                    callback,
                    help=help_text,
                )
