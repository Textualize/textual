from __future__ import annotations

from typing import Type
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import Header, Footer, Label
from textual.binding import Binding


class GridHeightAuto(App[None]):
    CSS = """
    #test-area {
        
        border: solid red;
        height: auto;
    }

    Grid {
        grid-size: 3;
        # grid-rows: auto;
    }
    """

    BINDINGS = [
        Binding("g", "grid", "Grid"),
        Binding("v", "vertical", "Vertical"),
        Binding("h", "horizontal", "Horizontal"),
        Binding("c", "container", "Container"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(Label("Select a container to test (see footer)"), id="sandbox")
        yield Footer()

    def build(self, out_of: Type[Container | Grid | Horizontal | Vertical]) -> None:
        self.query("#sandbox > *").remove()
        self.query_one("#sandbox", Vertical).mount(
            Label("Here is some text before the grid"),
            out_of(*[Label(f"Cell #{n}") for n in range(9)], id="test-area"),
            Label("Here is some text after the grid"),
        )

    def action_grid(self):
        self.build(Grid)

    def action_vertical(self):
        self.build(Vertical)

    def action_horizontal(self):
        self.build(Horizontal)

    def action_container(self):
        self.build(Container)


if __name__ == "__main__":
    GridHeightAuto().run()
