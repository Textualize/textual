from __future__ import annotations
from textual.app import App, ComposeResult
from textual.widgets import Footer


class BindingsApp(App):
    """Check dynamic actions are displayed in the footer."""

    BINDINGS = [
        ("a", "a", "A"),
        ("b", "b", "B"),
        ("c", "c", "C"),
    ]

    def compose(self) -> ComposeResult:
        yield Footer()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "b":
            # A is disabled (not show)
            return False
        if action == "c":
            # B is disabled (shown grayed out)
            return None
        # Everything else is fine
        return True

    def action_a(self):
        self.bell()

    def action_b(self):
        # If dynamic actions is working we won't get here
        1 / 0

    def action_c(self):
        # If dynamic actions is working we won't get here
        1 / 0


if __name__ == "__main__":
    BindingsApp().run()
