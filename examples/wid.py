from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Button, Footer


class MyWidget(Widget):
    def __init__(self):
        self.button = Button()
        super().__init__()

    def compose(self) -> ComposeResult:
        yield self.button


class MyApp(App):

    BINDINGS = [("s", "show_button", "Show Button")]

    def __init__(self):
        self.my_widget = None
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Footer()

    async def action_show_button(self) -> None:
        if self.my_widget is None:
            self.my_widget = MyWidget()
        else:
            await self.my_widget.remove()
        await self.mount(self.my_widget)


if __name__ == "__main__":
    app = MyApp()
    app.run()
