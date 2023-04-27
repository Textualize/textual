from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static


class ScreenSplitApp(App[None]):
    CSS = """
    Horizontal {
        width: 1fr;        
    }

    Vertical {
        width: 1fr;
        background: blue;
        min-width: 20;
    }

    #scroll1 {
        width: 1fr;
        background: $panel;
    }

    #scroll2 {
        width: 2fr;
        background: $panel;
    }

    Static {
        width: 1fr;
        content-align: center middle;
        background: $boost;
    }

    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Vertical()
            with VerticalScroll(id="scroll1"):
                for n in range(100):
                    yield Static(f"This is content number {n}")
            with VerticalScroll(id="scroll2"):
                for n in range(100):
                    yield Static(f"This is content number {n}")
        yield Footer()


if __name__ == "__main__":
    ScreenSplitApp().run()
