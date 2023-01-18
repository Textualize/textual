from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Label
from textual.containers import Vertical, Container


class Overlay(Container):
    def compose(self) -> ComposeResult:
        yield Label("This should float over the top")


class Body1(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("My God! It's full of stars! " * 300)


class Body2(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("My God! It's full of stars! " * 300)


class Good(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Overlay()
        yield Body1()
        yield Footer()


class Bad(Screen):
    def compose(self) -> ComposeResult:
        yield Overlay()
        yield Header()
        yield Body2()
        yield Footer()


class Layers(App[None]):

    CSS = """
    Screen {
        layers: base higher;
    }

    Overlay {
        layer: higher;
        dock: top;
        width: auto;
        height: auto;
        padding: 2;
        border: solid yellow;
        background: red;
        color: yellow;
    }

    Body2 {
        background: green;
    }
    """

    SCREENS = {"good": Good, "bad": Bad}

    BINDINGS = [("t", "toggle", "Toggle Screen")]

    def on_mount(self):
        self.push_screen("good")

    def action_toggle(self):
        self.switch_screen(
            "bad" if self.screen.__class__.__name__ == "Good" else "good"
        )


if __name__ == "__main__":
    Layers().run()
