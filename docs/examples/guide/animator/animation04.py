from rich.console import RenderableType

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widget import Widget


class ValueBox(Widget):
    value = reactive(0.0)

    def render(self) -> RenderableType:
        return str(self.value)


class AnimationApp(App):
    def compose(self) -> ComposeResult:
        self.box = ValueBox()
        self.box.styles.background = "red"
        self.box.styles.color = "black"
        self.box.styles.padding = (1, 2)
        yield self.box

    async def on_mount(self):
        self.box.animate("value", value=100.0, duration=100.0, easing="linear")


if __name__ == "__main__":
    app = AnimationApp()
    app.run()
