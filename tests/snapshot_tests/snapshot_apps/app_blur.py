from textual.app import App, ComposeResult
from textual.events import AppBlur
from textual.widgets import Input

class AppBlurApp(App[None]):

    CSS = """
    Screen {
        align: center middle;
    }

    Input {
        width: 50%;
        margin-bottom: 1;

        &:focus {
            width: 75%;
            border: thick green;
            background: pink;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Input("This should be the blur style")
        yield Input("This should also be the blur style")

    def on_mount(self) -> None:
        self.post_message(AppBlur())

if __name__ == "__main__":
    AppBlurApp().run()
