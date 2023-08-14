from textual.app import App, ComposeResult
from textual.widgets import Collapsible, Label


class CollapsibleApp(App):
    BINDINGS = [
        ("c", "collapse_or_expand(True)", "Collapse All"),
        ("e", "collapse_or_expand(False)", "Expand All"),
    ]

    def compose(self) -> ComposeResult:
        with Collapsible(title="",
                         collapsed_symbol="► Show more",
                         expanded_symbol="▼ Close"):
            yield Label("Many words.")

    def action_collapse_or_expand(self, collapse: bool) -> None:
        for child in self.walk_children(Collapsible):
            child.collapsed = collapse


if __name__ == "__main__":
    app = CollapsibleApp()
    app.run()
