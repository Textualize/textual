from textual.app import App, ComposeResult
from textual.widgets import Static

TEXT = """
[b]Set your background[/b]
[@click=app.set_background('red')]Red[/]
[@click=app.set_background('green')]Green[/]
[@click=app.set_background('blue')]Blue[/]
"""


class ActionsApp(App):
    def compose(self) -> ComposeResult:
        yield Static(TEXT)

    def action_set_background(self, color: str) -> None:
        self.screen.styles.background = color


if __name__ == "__main__":
    app = ActionsApp()
    app.run()
