from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Collapsible, Label


class CollapsibleApp(App[None]):
    def compose(self) -> ComposeResult:
        with Horizontal():
            with Collapsible(
                collapsed_symbol=">>>",
                expanded_symbol="v",
            ):
                yield Label("Hello, world.")

            with Collapsible(
                collapsed_symbol=">>>",
                expanded_symbol="v",
                collapsed=False,
            ):
                yield Label("Hello, world.")


if __name__ == "__main__":
    app = CollapsibleApp()
    app.run()
