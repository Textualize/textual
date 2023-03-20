#!/usr/bin/env python3

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static


class NestedAutoApp(App[None]):
    CSS = """
    Screen {
        background: red;
    }

    #my-static-container {
        border: heavy lightgreen;
        background: green;
        height: auto;
        max-height: 10;
    }

    #my-static-wrapper {
        border: heavy lightblue;
        background: blue;
        width: auto;
        height: auto;
    }

    #my-static {
        border: heavy gray;
        background: black;
        width: auto;
        height: auto;
    }
    """
    BINDINGS = [
        ("1", "1", "1"),
        ("2", "2", "2"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        self._static = Static("", id="my-static")
        yield VerticalScroll(
            VerticalScroll(
                self._static,
                id="my-static-wrapper",
            ),
            id="my-static-container",
        )

    def action_1(self) -> None:
        self._static.update(
            "\n".join(f"Lorem {i} Ipsum {i} Sit {i}" for i in range(1, 21))
        )

    def action_2(self) -> None:
        self._static.update("JUST ONE LINE")


if __name__ == "__main__":
    app = NestedAutoApp()
    app.run()
