from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Label, Input


class Dialog(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Label("Dialog")
        yield Input()
        yield Button("OK", id="ok")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.app.pop_screen()  # Never gets here


class ModalApp(App):
    BINDINGS = [("enter", "open_dialog", "Open Dialog")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Hello")
        yield Footer()

    def action_open_dialog(self) -> None:
        self.push_screen(Dialog())


if __name__ == "__main__":
    app = ModalApp()
    app.run()
