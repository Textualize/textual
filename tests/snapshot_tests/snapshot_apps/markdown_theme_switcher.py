from textual.app import App, ComposeResult
from textual.widgets import Markdown

TEST_CODE_MARKDOWN = """
# This is a H1
```python
def main():
    print("Hello world!")
```
"""


class MarkdownThemeSwitcherApp(App[None]):
    BINDINGS = [
        ("t", "toggle_theme"),
        ("d", "switch_dark"),
        ("l", "switch_light"),
    ]

    def action_switch_dark(self) -> None:
        md = self.query_one(Markdown)
        md.code_dark_theme = "solarized-dark"

    def action_switch_light(self) -> None:
        md = self.query_one(Markdown)
        md.code_light_theme = "solarized-light"

    def action_toggle_theme(self) -> None:
        self.theme = "textual-light" if self.theme == "textual-dark" else "textual-dark"

    def compose(self) -> ComposeResult:
        yield Markdown(TEST_CODE_MARKDOWN)


if __name__ == "__main__":
    MarkdownThemeSwitcherApp().run()
