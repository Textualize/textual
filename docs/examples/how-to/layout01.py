from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Placeholder


class Header(Placeholder):  # (1)!
    pass


class Footer(Placeholder):  # (2)!
    pass


class TweetScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(id="Header")  # (3)!
        yield Footer(id="Footer")  # (4)!


class LayoutApp(App):
    def on_mount(self) -> None:
        self.push_screen(TweetScreen())


if __name__ == "__main__":
    app = LayoutApp()
    app.run()
