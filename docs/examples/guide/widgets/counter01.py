from textual.app import App, ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widgets import Footer, Static


class Counter(Static, can_focus=True):  # (1)!
    """A counter that can be incremented and decremented by pressing keys."""

    count = reactive(0)

    def render(self) -> RenderResult:
        return f"Count: {self.count}"


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
