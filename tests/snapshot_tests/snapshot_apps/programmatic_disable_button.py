from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widgets import Button, Footer, Label


class ExampleApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    """

    BINDINGS = [("space", "toggle_button", "Toggle Button")]

    def compose(self) -> ComposeResult:
        with Center():
            yield Label("Hover the button then hit space")
        with Center():
            yield Button("Enabled", id="disable-btn")
        yield Footer()

    def action_toggle_button(self) -> None:
        self.app.bell()
        button = self.query_one("#disable-btn", Button)
        if button.disabled is False:
            button.disabled = True
            button.label = "Disabled"
        else:
            button.disabled = False
            button.label = "Enabled"


if __name__ == "__main__":
    app = ExampleApp()
    app.run()
