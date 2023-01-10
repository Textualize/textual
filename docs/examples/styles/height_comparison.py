from textual.app import App
from textual.containers import Vertical
from textual.widgets import Placeholder, Label, Static


class Ruler(Static):
    def compose(self):
        ruler_text = "·\n·\n·\n·\n•\n" * 100
        yield Label(ruler_text)


class HeightComparisonApp(App):
    def compose(self):
        yield Vertical(
            Placeholder(id="cells"),  # (1)!
            Placeholder(id="percent"),
            Placeholder(id="w"),
            Placeholder(id="h"),
            Placeholder(id="vw"),
            Placeholder(id="vh"),
            Placeholder(id="auto"),
            Placeholder(id="fr1"),
            Placeholder(id="fr2"),
        )
        yield Ruler()


app = HeightComparisonApp(css_path="height_comparison.css")
