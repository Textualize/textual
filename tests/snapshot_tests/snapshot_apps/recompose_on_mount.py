from __future__ import annotations

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, RadioSet
from textual.reactive import reactive


class Profile(Static):
    choices: reactive[list[str]] = reactive(list, recompose=True)

    def compose(self) -> ComposeResult:
        yield RadioSet(*self.choices)

    async def on_mount(self) -> None:
        self.choices.append("Foo")
        self.choices.append("Bar")
        self.mutate_reactive(Profile.choices)


class Landing(Screen):
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Static(" Profile ", id="title")
        yield Profile()
        yield Footer()


class ForecastApp(App):
    """A Textual app to forecast Financials."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.install_screen(Landing(), name="landing")
        self.push_screen("landing")


if __name__ == "__main__":
    app = ForecastApp()
    app.run()
