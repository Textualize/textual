from textual.app import App, ComposeResult
from textual.widgets import Rule, Label
from textual.widgets._rule import _VALID_LINE_STYLES, LineStyle
from typing import cast


class RuleApp(App):
    CSS = """
    Screen {
        align: center middle;
    }

    Rule {
        width: 80%;
    }

    Label {
        width: 80%;
        text-align: center;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        # TODO: This is just a temporary example to demonstrate and test the
        # different Rule styles. This will obviously need a nicer presentation
        # and _explicity_ created Rule widgets for the documentation.
        for line_style in sorted(_VALID_LINE_STYLES):
            yield Label(line_style)
            yield Rule(line_style=cast(LineStyle, line_style))


if __name__ == "__main__":
    app = RuleApp()
    app.run()
