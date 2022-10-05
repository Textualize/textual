from textual.app import App, ComposeResult
from textual.color import Color
from textual.widgets import Static


class ColorApp(App):
    def compose(self) -> ComposeResult:
        self.widgets = [Static("") for n in range(10)]
        yield from self.widgets

    def on_mount(self) -> None:
        for index, widget in enumerate(self.widgets, 1):
            alpha = index * 0.1
            widget.update(f"alpha={alpha:.1f}")
            widget.styles.background = Color(191, 78, 96, a=alpha)


if __name__ == "__main__":
    app = ColorApp()
    app.run()
