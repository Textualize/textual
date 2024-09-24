from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Static


class Counter(Static, can_focus=True):
    """A counter that can be incremented and decremented by pressing keys."""

    BINDINGS = [
        Binding("up", "change_count(1)", "Increment"),
        Binding("down", "change_count(-1)", "Decrement"),
    ]

    count = reactive(0)

    def render(self) -> str:
        return f"Count: {self.count}"

    def action_change_count(self, amount: int) -> None:
        self.count += amount


class CalculatorApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Counter()
        yield Counter()


if __name__ == "__main__":
    app = CalculatorApp()
    app.run()
