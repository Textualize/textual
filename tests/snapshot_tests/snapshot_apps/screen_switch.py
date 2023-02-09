from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Header, Footer


class ScreenA(Screen):
    BINDINGS = [("b", "switch_to_b", "Switch to screen B")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("A")
        yield Footer()

    def action_switch_to_b(self):
        self.app.switch_screen(ScreenB())


class ScreenB(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("B")
        yield Footer()


class ModalApp(App):
    BINDINGS = [("a", "push_a", "Push screen A")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_push_a(self) -> None:
        self.push_screen(ScreenA())


if __name__ == "__main__":
    app = ModalApp()
    app.run()
