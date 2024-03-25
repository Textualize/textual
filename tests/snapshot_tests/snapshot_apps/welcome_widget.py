from textual.app import App, ComposeResult
from textual.widgets import Welcome

class WelcomeApp(App[None]):

    def compose(self) -> ComposeResult:
        yield Welcome()

if __name__ == "__main__":
    WelcomeApp().run()
