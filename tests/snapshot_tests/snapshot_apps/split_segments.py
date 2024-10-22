from textual.app import App, ComposeResult
from textual.widgets import TextArea

FAIL_TEXT = "x"


class CodeApp(App):
    def compose(self) -> ComposeResult:
        yield TextArea(FAIL_TEXT, soft_wrap=False, show_line_numbers=True)


if __name__ == "__main__":
    app = CodeApp()
    app.run()
