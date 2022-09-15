from textual import layout
from textual.app import ComposeResult, App
from textual.widgets import Static, Header


class CombiningLayoutsExample(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield layout.Container(
            layout.Vertical(
                *[Static(f"Vertical layout, child {number}") for number in range(15)],
                id="left-pane",
            ),
            layout.Horizontal(
                Static("Horizontally"),
                Static("Positioned"),
                Static("Children"),
                Static("Here"),
                id="top-right",
            ),
            layout.Container(
                Static("This"),
                Static("panel"),
                Static("is"),
                Static("using"),
                Static("grid layout!", id="bottom-right-final"),
                id="bottom-right",
            ),
            id="app-grid",
        )

    async def on_key(self, event) -> None:
        await self.dispatch_key(event)

    def key_a(self):
        print(self.stylesheet.variables["boost"])
        print(self.stylesheet.variables["boost-lighten-1"])
        print(self.stylesheet.variables["boost-lighten-2"])


app = CombiningLayoutsExample(css_path="combining_layouts.css")
if __name__ == "__main__":
    app.run()
