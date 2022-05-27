from textual.app import App, ComposeResult
from textual.widget import Widget
from textual import layout


from rich.text import Text


lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

TEXT = Text.from_markup(lorem)


class TextWidget(Widget):
    def render(self):
        return TEXT


class AutoApp(App, css_path="nest.css"):
    def on_mount(self) -> None:
        self.bind("t", "tree")

    def compose(self) -> ComposeResult:
        yield layout.Vertical(
            Widget(
                TextWidget(classes="test"),
                id="container",
            ),
        )

    def action_tree(self):
        self.log(self.screen.tree)
