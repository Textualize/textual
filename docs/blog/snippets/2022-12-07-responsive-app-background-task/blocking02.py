import asyncio
import time
from random import randint

from textual.app import App, ComposeResult
from textual.color import Color
from textual.containers import Grid, VerticalScroll
from textual.widget import Widget
from textual.widgets import Footer, Label


class ColourChanger(Widget):
    def on_click(self) -> None:
        self.styles.background = Color(
            randint(1, 255),
            randint(1, 255),
            randint(1, 255),
        )


class MyApp(App[None]):
    BINDINGS = [("l", "load", "Load data")]
    CSS = """
    Grid {
        grid-size: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Grid(
            ColourChanger(),
            VerticalScroll(id="log"),
        )
        yield Footer()

    def action_load(self) -> None:  # (1)!
        asyncio.create_task(self._do_long_operation())  # (2)!

    async def _do_long_operation(self) -> None:  # (3)!
        time.sleep(5)
        self.query_one("#log").mount(Label("Data loaded ✅"))


MyApp().run()
