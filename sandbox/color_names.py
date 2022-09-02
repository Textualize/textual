import rich.repr
from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.pretty import Pretty

from textual._color_constants import COLOR_NAME_TO_RGB
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Placeholder


@rich.repr.auto(angular=False)
class ColorDisplay(Widget, can_focus=True):
    def render(self) -> RenderableType:
        return Panel(
            Align.center(
                Pretty(self, no_wrap=True, overflow="ellipsis"), vertical="middle"
            ),
            title=self.name,
            border_style="none",
        )


class ColorNames(App):
    DEFAULT_CSS = """
    ColorDisplay {
        height: 1;
    }
    """

    def on_mount(self):
        self.bind("q", "quit")

    def compose(self) -> ComposeResult:
        for color_name, color in COLOR_NAME_TO_RGB.items():
            color_placeholder = ColorDisplay(name=color_name)
            is_dark_color = sum(color) < 400
            color_placeholder.styles.color = "white" if is_dark_color else "black"
            color_placeholder.styles.background = color_name
            yield color_placeholder


if __name__ == "__main__":
    color_name_app = ColorNames()
    color_name_app.run()
