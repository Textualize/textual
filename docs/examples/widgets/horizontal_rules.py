from textual.app import App, ComposeResult
from textual.widgets import Rule, Label
from textual.containers import Vertical


class HorizontalRulesApp(App):
    CSS = """
    Screen {
        align: center middle;
    }

    Vertical {
        height: auto;
        width: 80%;
    }

    Label {
        width: 100%;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("solid (default)")
            yield Rule()
            yield Label("heavy")
            yield Rule(line_style="heavy")
            yield Label("thick")
            yield Rule(line_style="thick")
            yield Label("blank/hidden/none")
            yield Rule(line_style="hidden")
            yield Label("dashed")
            yield Rule(line_style="dashed")
            yield Label("double")
            yield Rule(line_style="double")
            yield Label("ascii")
            yield Rule(line_style="ascii")


if __name__ == "__main__":
    app = HorizontalRulesApp()
    app.run()
