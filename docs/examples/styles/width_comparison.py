from textual.app import App
from textual.containers import Horizontal
from textual.widgets import Label, Placeholder, Static


class Ruler(Static):
    def compose(self):
        ruler_text = "····•" * 100
        yield Label(ruler_text)


class WidthComparisonApp(App):
    def compose(self):
        yield Horizontal(
            Placeholder(id="cells"),  # (1)!
            Placeholder(id="percent"),
            Placeholder(id="w"),
            Placeholder(id="h"),
            Placeholder(id="vw"),
            Placeholder(id="vh"),
            Placeholder(id="auto"),
            Placeholder(id="fr1"),
            Placeholder(id="fr3"),
        )
        yield Ruler()


app = WidthComparisonApp(css_path="width_comparison.css")
if __name__ == "__main__":
    app.run()
