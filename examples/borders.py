from itertools import cycle

from textual.app import App
from textual.color import Color
from textual.constants import BORDERS
from textual.widgets import Static


class BorderApp(App):
    """Displays a pride flag."""

    COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]

    def compose(self):
        self.dark = True
        for border, color in zip(BORDERS, cycle(self.COLORS)):
            static = Static(f"border: {border} {color};")
            static.styles.height = 7
            static.styles.background = Color.parse(color).with_alpha(0.2)
            static.styles.margin = (1, 2)
            static.styles.border = (border, color)
            static.styles.content_align = ("center", "middle")
            yield static


app = BorderApp()

if __name__ == "__main__":
    app.run()
