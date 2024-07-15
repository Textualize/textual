from textual.app import App, ComposeResult
from textual.scroll_view import ScrollView
from textual.strip import Strip
from rich.segment import Segment


class LineWidget(ScrollView):
    COMPONENT_CLASSES = {"faded"}

    DEFAULT_CSS = """
    LineWidget {
        background:blue;
        color:white;
        &>.faded{
            text-opacity:0.5;
          
        }
    }
    """

    def render_line(self, y: int) -> Strip:
        style = self.get_component_rich_style("faded")
        return Strip([Segment("W" * self.size.width, style)])


class TestApp(App):
    def compose(self) -> ComposeResult:
        yield LineWidget()


if __name__ == "__main__":
    app = TestApp()
    app.run()
