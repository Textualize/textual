from rich.console import RenderableType

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import OptionList


class SimpleLoadingIndicator(Widget):
    """A loading indicator that doesn't animate."""

    DEFAULT_CSS = """
    SimpleLoadingIndicator {
        width: 100%;
        height: 100%;
        min-height: 1;
        content-align: center middle;
        color: $secondary;        
    }
    SimpleLoadingIndicator.-textual-loading-indicator {
        layer: _loading;
        background: $boost;     
        dock: top;
    }
    """

    def render(self) -> RenderableType:
        return "Loading!"


class LoadingOverlayRedux(App[None]):
    CSS = """
    OptionList {
        scrollbar-gutter: stable;
        width: 1fr;
        height: 1fr;
    }
    """

    BINDINGS = [("space", "toggle")]

    def get_loading_widget(self) -> Widget:
        return SimpleLoadingIndicator()

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield OptionList(*[("hello world " * 5) for _ in range(100)])
            yield OptionList(*[("foo bar" * 5) for _ in range(100)])

    def action_toggle(self) -> None:
        option_list = self.query(OptionList).first()
        option_list.loading = not option_list.loading


if __name__ == "__main__":
    LoadingOverlayRedux().run()
