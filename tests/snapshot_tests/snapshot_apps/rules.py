from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Rule

RULE_STYLES = [
    "ascii",
    "blank",
    "dashed",
    "double",
    "heavy",
    "hidden",
    "none",
    "solid",
    "thick",
]


class RuleApp(App):
    def compose(self) -> ComposeResult:
        with Vertical():
            for rule_style in RULE_STYLES:
                yield Rule(line_style=rule_style)

        with Horizontal():
            for rule_style in RULE_STYLES:
                yield Rule("vertical", line_style=rule_style)


if __name__ == "__main__":
    RuleApp().run()
