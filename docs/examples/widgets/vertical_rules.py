from textual.app import App, ComposeResult
from textual.widgets import Rule, Label
from textual.containers import Horizontal


class VerticalRulesApp(App):
    CSS_PATH = "vertical_rules.tcss"

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label("solid (default)")
            yield Rule(orientation="vertical")
            yield Label("heavy")
            yield Rule(orientation="vertical", line_style="heavy")
            yield Label("thick")
            yield Rule(orientation="vertical", line_style="thick")
            yield Label("blank /hidden /none")
            yield Rule(orientation="vertical", line_style="hidden")
            yield Label("dashed")
            yield Rule(orientation="vertical", line_style="dashed")
            yield Label("double")
            yield Rule(orientation="vertical", line_style="double")
            yield Label("ascii")
            yield Rule(orientation="vertical", line_style="ascii")


if __name__ == "__main__":
    app = VerticalRulesApp()
    app.run()
