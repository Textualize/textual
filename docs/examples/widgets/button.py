from textual.app import App, ComposeResult
from textual.widgets import Button


class ButtonsApp(App):
    def compose(self) -> ComposeResult:
        yield Button("Default", id="foo")
        yield Button("Disabled", disabled=True)
        yield Button.success("Success!")
        yield Button.warning("Warning!")
        yield Button.error("Error!")

    def on_button_pressed(self, _event: Button.Pressed) -> None:
        self.app.bell()


app = ButtonsApp(css_path="button.css")

if __name__ == "__main__":
    result = app.run()
