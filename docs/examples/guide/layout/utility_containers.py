from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Static


class UtilityContainersExample(App):
    CSS_PATH = "utility_containers.css"

    def compose(self) -> ComposeResult:
        yield Horizontal(
            VerticalScroll(
                Static("One"),
                Static("Two"),
                classes="column",
            ),
            VerticalScroll(
                Static("Three"),
                Static("Four"),
                classes="column",
            ),
        )


if __name__ == "__main__":
    app = UtilityContainersExample()
    app.run()
