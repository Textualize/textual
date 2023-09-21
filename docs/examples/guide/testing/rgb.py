from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Footer


class RGBApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    Horizontal {
        width: auto;
        height: auto;
    }
    """

    BINDINGS = [
        ("r", "switch_color('red')", "Go Red"),
        ("g", "switch_color('green')", "Go Green"),
        ("b", "switch_color('blue')", "Go Blue"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Button("Red", id="red")
            yield Button("Green", id="green")
            yield Button("Blue", id="blue")
        yield Footer()

    @on(Button.Pressed)
    def pressed_button(self, event: Button.Pressed) -> None:
        assert event.button.id is not None
        self.action_switch_color(event.button.id)

    def action_switch_color(self, color: str) -> None:
        self.screen.styles.background = color


if __name__ == "__main__":
    app = RGBApp()
    app.run()
