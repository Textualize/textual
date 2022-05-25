from rich.padding import Padding
from rich.style import Style
from rich.text import Text

from textual.app import App
from textual.renderables.gradient import VerticalGradient
from textual.widget import Widget

lorem = Text.from_markup(
    """[#C5CAE9]Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit libero, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum. In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit libero, volutpat nec hendrerit at, faucibus in odio. Aliquam hendrerit nibh sed quam volutpat maximus. Nullam suscipit convallis lorem quis sodales. In tristique lobortis ante et dictum. Ut at finibus ipsum. In urna dolor, placerat et mi facilisis, congue sollicitudin massa. Phasellus felis turpis, cursus eu lectus et, porttitor malesuada augue. Sed feugiat volutpat velit, sollicitudin fringilla velit bibendum faucibus. """,
    justify="full",
)


class Lorem(Widget):
    def render(self) -> Text:
        return Padding(lorem, 1)


class Background(Widget):
    def render(self):
        return VerticalGradient("#212121", "#212121")


class BordersApp(App):
    """Sandbox application used for testing/development by Textual developers"""

    def on_load(self):
        self.bind("q", "quit", "Quit")

    def on_mount(self):
        """Build layout here."""

        borders = [
            Lorem(classes={"border", border})
            for border in (
                "round",
                "solid",
                "double",
                "dashed",
                "heavy",
                "inner",
                "outer",
                "hkey",
                "vkey",
                "tall",
                "wide",
            )
        ]
        borders_view = Background(*borders)
        borders_view.show_vertical_scrollbar = True

        self.mount(borders=borders_view)


app = BordersApp(css_path="borders.css", log_path="textual.log")
app.run()
