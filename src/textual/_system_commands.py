"""A command palette command provider for Textual system commands.

This is a simple command provider that makes the most obvious application
actions available via the [command palette][textual.command.CommandPalette].
"""

from .command import Hit, Hits, Provider


class SystemCommands(Provider):
    """A [source][textual.command.Provider] of command palette commands that run app-wide tasks.

    Used by default in [`App.COMMANDS`][textual.app.App.COMMANDS].
    """

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
        for name, runnable, help_text in (
            (
                "Toggle light/dark mode",
                self.app.action_toggle_dark,
                "Toggle the application between light and dark mode",
            ),
            (
                "Quit the application",
                self.app.action_quit,
                "Quit the application as soon as possible",
            ),
            (
                "Ring the bell",
                self.app.action_bell,
                "Ring the terminal's 'bell'",
            ),
        ):
            match = matcher.match(name)
            if match > 0:
                yield Hit(
                    match,
                    matcher.highlight(name),
                    runnable,
                    help=help_text,
                )
