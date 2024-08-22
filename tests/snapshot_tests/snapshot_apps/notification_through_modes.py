from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label

class Mode(Screen):

    def compose(self) -> ComposeResult:
        yield Label("This is a mode screen")


class NotifyThroughModesApp(App[None]):

    MODES = {
        "test": Mode
    }

    def compose(self) -> ComposeResult:
        yield Label("Base screen")

    def on_mount(self):
        for n in range(10):
            self.notify(str(n))
        self.switch_mode("test")

if __name__ == "__main__":
    NotifyThroughModesApp().run()
