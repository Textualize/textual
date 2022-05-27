from rich.style import Style

from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Static


class Thing(Widget):
    def render(self):
        return "Hello, 3434 World.\n[b]Lorem impsum."


class AlignApp(App):
    def on_load(self):
        self.bind("t", "log_tree")

    def compose(self) -> ComposeResult:
        yield Thing(id="thing")
        yield Static("foo", id="thing2")
        yield Widget(id="thing3")

    def action_log_tree(self):
        self.log(self.screen.tree)


app = AlignApp(css_path="align.css")

if __name__ == "__main__":
    app.run()
