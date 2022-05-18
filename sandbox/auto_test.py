from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.layout import Vertical

from rich.text import Text

TEXT = Text.from_markup(" ".join(str(n) * 5 for n in range(12)))


class AutoApp(App):
    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(TEXT, classes="test"), Static(TEXT, id="test", classes="test")
        )


app = AutoApp(css_path="auto_test.css")

if __name__ == "__main__":
    app.run()
