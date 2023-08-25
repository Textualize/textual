from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Footer, Label

if TYPE_CHECKING:
    from rich.console import RenderableType


class NestedLabel(Widget):
    DEFAULT_CSS = """
    NestedLabel {
        height: auto;
    }
    """

    def __init__(
        self,
        renderable: RenderableType,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)

        self.__label = Label(renderable, id=f"{id}--label")

    def compose(self) -> ComposeResult:
        yield self.__label


class MyApp(App):
    CSS = """
    #label, #nested-label Label {
        padding: 1;
        text-align: center;
        width: 1fr;
    }

    #label {
        background: green;
    }

    #nested-label {
        background: red;
    }

    """

    def compose(self) -> ComposeResult:
        yield Label("label", id="label")
        yield NestedLabel("nested label", id="nested-label")
        yield Footer()


if __name__ == "__main__":
    MyApp().run()
