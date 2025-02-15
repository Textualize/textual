from __future__ import annotations

from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Grid
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Label


class QuitScreen(ModalScreen[bool]):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.dismiss(True)
        else:
            self.dismiss(False)


class ModalApp(App):
    """An app with a modal dialog."""

    BINDINGS = [("q", "request_quit", "Quit")]

    def __init__(self) -> None:
        self.check_quit_called = False
        super().__init__()

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand(
            "try a modal quit dialog", "this should work", self.action_request_quit
        )

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""

        def check_quit(quit: bool | None) -> None:
            """Called when QuitScreen is dismissed."""
            self.check_quit_called = True

        self.push_screen(QuitScreen(), check_quit)


async def test_command_dismiss():
    """Regression test for https://github.com/Textualize/textual/issues/5512"""
    app = ModalApp()

    async with app.run_test() as pilot:
        await pilot.press("ctrl+p", *"modal quit", "enter")
        await pilot.pause()
        await pilot.press("enter")
        assert app.check_quit_called
