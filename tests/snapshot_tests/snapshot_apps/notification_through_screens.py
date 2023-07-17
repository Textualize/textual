from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label

class StackableScreen(Screen):

    TARGET_DEPTH = 10

    def __init__(self, count:int = TARGET_DEPTH) -> None:
        super().__init__()
        self._number = count

    def compose(self) -> ComposeResult:
        yield Label(f"Screen {self.TARGET_DEPTH - self._number}")

    def on_mount(self) -> None:
        if self._number > 0:
            self.app.push_screen(StackableScreen(self._number - 1))

class NotifyDownScreensApp(App[None]):

    def compose(self) -> ComposeResult:
        yield Label("Base screen")

    def on_mount(self):
        for n in range(10):
            self.notify(str(n))
        self.push_screen(StackableScreen())

if __name__ == "__main__":
    NotifyDownScreensApp().run()
