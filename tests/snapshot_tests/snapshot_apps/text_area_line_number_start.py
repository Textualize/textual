from textual.app import App, ComposeResult
from textual.widgets import TextArea

TEXT = """\
Foo
Bar
Baz
"""


class LineNumbersReactive(App[None]):
    START_LINE_NUMBER = 9999

    def compose(self) -> ComposeResult:
        yield TextArea(
            TEXT,
            soft_wrap=True,
            show_line_numbers=True,
            line_number_start=self.START_LINE_NUMBER,
        )


app = LineNumbersReactive()
if __name__ == "__main__":
    app.run()
