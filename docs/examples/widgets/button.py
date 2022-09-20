from textual import layout
from textual.app import App, ComposeResult
from textual.widgets import Button, Static


class ButtonsApp(App[str]):
    CSS_PATH = "button.css"

    def compose(self) -> ComposeResult:
        yield layout.Horizontal(
            layout.Vertical(
                Static("Standard Buttons", classes="header"),
                Button("Default"),
                Button("Primary!", variant="primary"),
                Button.success("Success!"),
                Button.warning("Warning!"),
                Button.error("Error!"),
            ),
            layout.Vertical(
                Static("Disabled Buttons", classes="header"),
                Button("Default", disabled=True),
                Button("Primary!", variant="primary", disabled=True),
                Button.success("Success!", disabled=True),
                Button.warning("Warning!", disabled=True),
                Button.error("Error!", disabled=True),
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.bell()
        self.exit(str(event.button))


if __name__ == "__main__":
    app = ButtonsApp()
    print(app.run())
