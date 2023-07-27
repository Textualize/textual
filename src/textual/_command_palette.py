"""The Textual command palette."""

from . import on
from .app import ComposeResult
from .binding import Binding
from .reactive import var
from .screen import ModalScreen
from .widgets import Input, OptionList


class CommandList(OptionList, can_focus=False):
    """The command palette command list."""

    DEFAULT_CSS = """
    CommandList {
        visibility: hidden;
        max-height: 50%;
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
    """

    BINDINGS = [
        Binding("escape", "escape", "Exit the command palette"),
        Binding("down", "command('cursor_down')", show=False),
        Binding("pagedown", "command('page_down')", show=False),
        Binding("pageup", "command('page_up')", show=False),
        Binding("up", "command('cursor_up')", show=False),
    ]

    placeholder: var[str] = var("Textual spotlight search", init=False)
    """The placeholder text for the command palette input."""

    def compose(self) -> ComposeResult:
        """Compose the command palette."""
        yield CommandInput(placeholder=self.placeholder)
        yield CommandList(*[f"{n} This is a test {n}" for n in range(500)])

    def _watch_placeholder(self) -> None:
        """Pass the new placeholder text down to the `CommandInput`."""
        self.query_one(CommandInput).placeholder = self.placeholder

    @on(Input.Changed)
    def input(self, event: Input.Changed) -> None:
        """React to input in the command palette.

        Args:
            event: The input event.
        """
        self.query_one(CommandList).set_class(bool(event.value), "--visible")

    def action_escape(self) -> None:
        """Handle a request to escape out of the command palette."""
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
