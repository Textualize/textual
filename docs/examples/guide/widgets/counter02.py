from textual.app import App, ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widgets import Footer, Static


class Counter(Static, can_focus=True):
    """A counter that can be incremented and decremented by pressing keys."""

    BINDINGS = [
        ("up,k", "change_count(1)", "Increment"),  # (1)!
        ("down,j", "change_count(-1)", "Decrement"),
    ]

    count = reactive(0)

    def render(self) -> RenderResult:
        return f"Count: {self.count}"

    def action_change_count(self, amount: int) -> None:  # (2)!
        self.count += amount


class CounterApp(App[None]):
    CSS_PATH = "counter.tcss"

    def compose(self) -> ComposeResult:
        yield Counter()
        yield Counter()
        yield Counter()
        yield Footer()


if __name__ == "__main__":
    app = CounterApp()
    app.run()
