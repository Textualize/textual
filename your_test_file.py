from textual.app import App, ComposeResult, RenderResult
from textual.containers import Horizontal
from textual.widgets import Header


class MiddleOfDisplay(Horizontal):

    DEFAULT_CSS = """
    MiddleOfDisplay {
        content-align: center middle;
        height: 1;
    }
    """

    def render(self) -> RenderResult:
        return "Title - Title"

class HeaderCheckApp(App[None]):

    TITLE = "Title"
    SUB_TITLE = "Title"

    def compose(self) -> ComposeResult:
        yield Header()
        yield MiddleOfDisplay()

if __name__ == "__main__":
    HeaderCheckApp().run()