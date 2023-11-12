from textual.app import App
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Placeholder


class VisibilityContainersApp(App):
    CSS_PATH = "visibility_containers.tcss"

    def compose(self):
        yield VerticalScroll(
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


if __name__ == "__main__":
    app = VisibilityContainersApp()
    app.run()
