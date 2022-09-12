from textual.app import App, ComposeResult
from textual.color import Color
from textual.widgets import Static


class ColorApp(App):
    def compose(self) -> ComposeResult:
        self.widgets = [Static(f"Textual {n+1}") for n in range(10)]
        yield from self.widgets

    def on_mount(self) -> None:
        for index, widget in enumerate(self.widgets, 1):
            widget.styles.background = Color(191, 78, 96, index * 0.1)


app = ColorApp()
if __name__ == "__main__":
    app.run()
