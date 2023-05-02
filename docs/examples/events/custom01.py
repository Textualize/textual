from textual.app import App, ComposeResult
from textual.color import Color
from textual.message import Message
from textual.widgets import Static


class ColorButton(Static):
    """A color button."""

    class Selected(Message):
        """Color selected message."""

        def __init__(self, color: Color) -> None:
            self.color = color
            super().__init__()

    def __init__(self, color: Color) -> None:
        self.color = color
        super().__init__()

    def on_mount(self) -> None:
        self.styles.margin = (1, 2)
        self.styles.content_align = ("center", "middle")
        self.styles.background = Color.parse("#ffffff33")
        self.styles.border = ("tall", self.color)

    def on_click(self) -> None:
        # The post_message method sends an event to be handled in the DOM
        self.post_message(self.Selected(self.color))

    def render(self) -> str:
        return str(self.color)


class ColorApp(App):
    def compose(self) -> ComposeResult:
        yield ColorButton(Color.parse("#008080"))
        yield ColorButton(Color.parse("#808000"))
        yield ColorButton(Color.parse("#E9967A"))
        yield ColorButton(Color.parse("#121212"))

    def on_color_button_selected(self, message: ColorButton.Selected) -> None:
        self.screen.styles.animate("background", message.color, duration=0.5)


if __name__ == "__main__":
    app = ColorApp()
    app.run()
