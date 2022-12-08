from textual.app import App, ComposeResult
from textual.widgets import Static


class AnimationApp(App):
    def compose(self) -> ComposeResult:
        self.box = Static("Hello, World!")
        self.box.styles.background = "red"
        self.box.styles.color = "black"
        self.box.styles.padding = (1, 2)
        yield self.box


if __name__ == "__main__":
    app = AnimationApp()
    app.run()
