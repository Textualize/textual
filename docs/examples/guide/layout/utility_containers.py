from textual import layout
from textual.app import App, ComposeResult
from textual.widgets import Static


class UtilityContainersExample(App):
    def compose(self) -> ComposeResult:
        yield layout.Horizontal(
            layout.Vertical(
                Static("One"),
                Static("Two"),
                classes="column",
            ),
            layout.Vertical(
                Static("Three"),
                Static("Four"),
                classes="column",
            ),
        )


app = UtilityContainersExample(css_path="utility_containers.css")
if __name__ == "__main__":
    app.run()
