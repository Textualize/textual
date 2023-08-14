from textual.app import App, ComposeResult
from textual.widgets import Collapsible


class CollapsibleApp(App):
    def compose(self) -> ComposeResult:
        with Collapsible(collapsed=False):
            yield Collapsible()


if __name__ == "__main__":
    app = CollapsibleApp()
    app.run()
