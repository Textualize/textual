from textual.app import App
from textual.containers import Horizontal, Vertical
from textual.widgets import Placeholder


class VisibilityContainersApp(App):
    def compose(self):
        yield Vertical(
            Horizontal(
                Placeholder(),
                Placeholder(),
                Placeholder(),
                id="top",
            ),
            Horizontal(
                Placeholder(),
                Placeholder(),
                Placeholder(),
                id="middle",
            ),
            Horizontal(
                Placeholder(),
                Placeholder(),
                Placeholder(),
                id="bot",
            ),
        )


app = VisibilityContainersApp(css_path="visibility_containers.css")
