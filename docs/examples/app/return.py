from textual.app import App, ComposeResult
from textual.widgets import Button


class ButtonsApp(App):
    def compose(self) -> ComposeResult:
        yield Button("Paul")
        yield Button("Duncan")
        yield Button("Chani")


app = ButtonsApp()
if __name__ == "__main__":
    app.run()
