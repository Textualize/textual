from textual.app import App, ComposeResult
from textual.widgets import Button


class ButtonsWithMarkupApp(App):
    def compose(self) -> ComposeResult:
        yield Button("[italic red]Focused[/] Button")
        yield Button("[italic red]Blurred[/] Button")
        yield Button("[italic red]Disabled[/] Button", disabled=True)


if __name__ == "__main__":
    app = ButtonsWithMarkupApp()
    app.run()
