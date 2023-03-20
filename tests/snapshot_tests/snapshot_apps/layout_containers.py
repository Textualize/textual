"""
App to test layout containers.
"""

from typing import Iterable

from textual.app import App, ComposeResult
from textual.containers import (
    Grid,
    Horizontal,
    HorizontalScroll,
    Vertical,
    VerticalScroll,
)
from textual.widget import Widget
from textual.widgets import Button, Input, Label


def sub_compose() -> Iterable[Widget]:
    yield Button.success("Accept")
    yield Button.error("Decline")
    yield Input()
    yield Label("\n\n".join([str(n * 1_000_000) for n in range(10)]))


class MyApp(App[None]):
    CSS = """
    Grid {
        grid-size: 2 2;
        grid-rows: 1fr;
        grid-columns: 1fr;
    }
    Grid > Widget {
        width: 100%;
        height: 100%;
    }
    Input {
        width: 80;
    }
    """

    def compose(self) -> ComposeResult:
        with Grid():
            with Horizontal():
                yield from sub_compose()
            with HorizontalScroll():
                yield from sub_compose()
            with Vertical():
                yield from sub_compose()
            with VerticalScroll():
                yield from sub_compose()


app = MyApp()
if __name__ == "__main__":
    app.run()
