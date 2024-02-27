from textual._easing import DEFAULT_EASING, EASING
from textual.app import App, ComposeResult
from textual.widgets import Static

ease = EASING[DEFAULT_EASING]


class AnimationApp(App):
    def compose(self) -> ComposeResult:
        self.box = Static("Hello, World!")
        self.box.styles.background = "red"
        self.box.styles.color = "black"
        self.box.styles.padding = (1, 2)
        yield self.box

    def key_1(self):
        self.box.styles.opacity = 1 - ease(0.25)

    def key_2(self):
        self.box.styles.opacity = 1 - ease(0.5)

    def key_3(self):
        self.box.styles.opacity = 1 - ease(0.75)


if __name__ == "__main__":
    app = AnimationApp()
    app.run()
