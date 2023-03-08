from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Static


class UtilityContainersExample(App):
    CSS_PATH = "utility_containers.css"

    def compose(self) -> ComposeResult:
        with Horizontal():
            with VerticalScroll(classes="column"):
                yield Static("One")
                yield Static("Two")
            with VerticalScroll(classes="column"):
                yield Static("Three")
                yield Static("Four")


if __name__ == "__main__":
    app = UtilityContainersExample()
    app.run()
