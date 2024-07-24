from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Label

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class QuitScreen(ModalScreen[bool]):  # (1)!
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

    CSS = """
QuitScreen {
    align: center middle;
}

#dialog {
    grid-size: 2;
    grid-gutter: 1 2;
    grid-rows: 1fr 3;
    padding: 0 1;
    width: 60;
    height: 11;
    border: thick $background 80%;
    background: $surface;
}

#question {
    column-span: 2;
    height: 1fr;
    width: 1fr;
    content-align: center middle;
}

Button {
    width: 100%;
}

    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(TEXT * 8)
        yield Footer()

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""

        def check_quit(quit: bool | None) -> None:
            """Called when QuitScreen is dismissed."""

            if quit:
                self.exit()

        self.push_screen(QuitScreen(), check_quit)


async def test_modal_pop_screen():
    # https://github.com/Textualize/textual/issues/4656

    async with ModalApp().run_test() as pilot:
        await pilot.pause()
        # Check clicking the footer brings up the quit screen
        await pilot.click(Footer)
        assert isinstance(pilot.app.screen, QuitScreen)
        # Check activating the quit button exits the app
        await pilot.press("enter")
        assert pilot.app._exit
