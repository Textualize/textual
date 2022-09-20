from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.layout import Vertical

from rich.text import Text

TEXT = Text.from_markup(" ".join(str(n) * 5 for n in range(12)))


class AutoApp(App):
    CSS_PATH = "auto_test.css"

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(TEXT, classes="test"), Static(TEXT, id="test", classes="test")
        )


if __name__ == "__main__":
    app = AutoApp()
    app.run()
