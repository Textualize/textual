from rich.text import Text

from textual.app import App, ComposeResult, RenderResult
from textual.containers import VerticalScroll
from textual.widgets import Header, Footer
from textual.widget import Widget


class Tester(Widget, can_focus=True):
    COMPONENT_CLASSES = {"tester--text"}

    DEFAULT_CSS = """
    Tester {
        height: auto;
    }
    
    Tester:focus > .tester--text {
        background: red;
    }
    """

    def __init__(self, n: int) -> None:
        self.n = n
        super().__init__()

    def render(self) -> RenderResult:
        return Text(
            f"test widget {self.n}", style=self.get_component_rich_style("tester--text")
        )


class StyleBugApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            for n in range(40):
                yield Tester(n)
        yield Footer()


if __name__ == "__main__":
    StyleBugApp().run()
