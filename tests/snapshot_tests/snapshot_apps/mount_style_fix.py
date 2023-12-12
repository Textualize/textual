from textual import __version__
from textual.app import App, ComposeResult
from textual.widgets import Static


# Regression test for https://github.com/Textualize/textual/issues/3858
class BrokenClassesApp(App[None]):
    CSS = """
    Screen {
        align: center middle;
    }

    Static {
        width: 50%;
        height: 50%;
        border: solid;
    }

    Screen.go-red Static {
        background: red;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(f"This should have a red background\n\nTextual {__version__}")

    def on_mount(self) -> None:
        self.screen.set_class(True, "go-red")


if __name__ == "__main__":
    BrokenClassesApp().run()
