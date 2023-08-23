from textual.app import App, ComposeResult
from textual.widgets import Collapsible
from textual.widgets import Label
from textual.containers import Horizontal, Vertical

class CollapsibleApp(App):

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Collapsible(title="", id="eh",
                            collapsed_symbol="▷ Show more",
                            expanded_symbol="∇ Close"):
                yield Label("Many words.")

            with Collapsible(title="",
                            collapsed_symbol="▷ Show more",
                            expanded_symbol="∇ Close",
                            collapsed=False):
                yield Label("Many words.")
                

if __name__ == "__main__":
    app = CollapsibleApp()
    app.run()
