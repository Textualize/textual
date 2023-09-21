from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Rule


class HorizontalRulesApp(App):
    CSS_PATH = "horizontal_rules.tcss"

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("solid (default)")
            yield Rule()
            yield Label("heavy")
            yield Rule(line_style="heavy")
            yield Label("thick")
            yield Rule(line_style="thick")
            yield Label("dashed")
            yield Rule(line_style="dashed")
            yield Label("double")
            yield Rule(line_style="double")
            yield Label("ascii")
            yield Rule(line_style="ascii")


if __name__ == "__main__":
    app = HorizontalRulesApp()
    app.run()
