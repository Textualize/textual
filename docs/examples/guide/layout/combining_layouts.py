from textual.containers import Container, Horizontal, Vertical
from textual.app import ComposeResult, App
from textual.widgets import Static, Header


class CombiningLayoutsExample(App):
    CSS_PATH = "combining_layouts.css"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                *[Static(f"Vertical layout, child {number}") for number in range(15)],
                id="left-pane",
            ),
            Horizontal(
                Static("Horizontally"),
                Static("Positioned"),
                Static("Children"),
                Static("Here"),
                id="top-right",
            ),
            Container(
                Static("This"),
                Static("panel"),
                Static("is"),
                Static("using"),
                Static("grid layout!", id="bottom-right-final"),
                id="bottom-right",
            ),
            id="app-grid",
        )


if __name__ == "__main__":
    app = CombiningLayoutsExample()
    app.run()
