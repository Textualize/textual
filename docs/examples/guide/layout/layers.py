from textual.app import App, ComposeResult
from textual.widgets import Static


class LayersExample(App):
    def compose(self) -> ComposeResult:
        yield Static("box1 (layer = above)", id="box1")
        yield Static("box2 (layer = below)", id="box2")


app = LayersExample(css_path="layers.css")
if __name__ == "__main__":
    app.run()
