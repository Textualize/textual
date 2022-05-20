from textual.app import App, ComposeResult
from textual.widgets import Static
from textual import layout

from rich.text import Text

TEXT = Text.from_markup(" ".join(str(n) * 5 for n in range(10)))


class AutoApp(App):
    def on_mount(self) -> None:
        self.bind("t", "tree")

    def compose(self) -> ComposeResult:
        yield layout.Horizontal(
            layout.Vertical(
                Static(TEXT, classes="test"),
                Static(TEXT, id="test", classes="test"),
            )
        )

    def action_tree(self):
        self.log(self.screen.tree)


app = AutoApp(css_path="vertical.css")

if __name__ == "__main__":
    app.run()
