from rich.text import Text

from textual.app import App
from textual.widget import Widget
from textual.widgets import Static


class Thing(Widget):
    def render(self):
        return Text.from_markup("Hello, World. [b magenta]Lorem impsum.")


class AlignApp(App):
    def on_load(self):
        self.bind("t", "log_tree")

    def on_mount(self) -> None:
        self.log("MOUNTED")
        self.mount(thing=Thing(), thing2=Static("0123456789"), thing3=Widget())

    def action_log_tree(self):
        self.log(self.screen.tree)


AlignApp.run(css_file="align.css", log="textual.log", watch_css=True)
