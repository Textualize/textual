from textual.app import App, ComposeResult
from textual.widgets import Rule, Label
from textual.widgets._rule import _VALID_LINE_STYLES, LineStyle
from typing import cast
from textual.containers import Horizontal


class RuleApp(App):
    CSS = """
    Screen {
        align: center middle;
    }

    Horizontal {
        width: 80%;
        height: 80%;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        # TODO: This is just a temporary example to demonstrate and test the
        # different Rule styles. This will obviously need a nicer presentation
        # and _explicity_ created Rule widgets for the documentation.
        with Horizontal():
            for line_style in sorted(_VALID_LINE_STYLES):
                yield Label(line_style)
                yield Rule(
                    orientation="vertical", line_style=cast(LineStyle, line_style)
                )


if __name__ == "__main__":
    app = RuleApp()
    app.run()
