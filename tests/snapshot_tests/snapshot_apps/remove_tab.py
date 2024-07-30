from textual.app import App
from textual.binding import Binding
from textual.widgets import Label, TabbedContent, TabPane


class ReproApp(App[None]):
    BINDINGS = [
        Binding("space", "close_pane"),
    ]

    def __init__(self):
        super().__init__()
        self.animation_level = "none"

    def compose(self):
        with TabbedContent():
            yield TabPane("foo1", Label("foo contents"))
            yield TabPane("bar22", Label("bar contents"))
            yield TabPane("baz333", Label("baz contents"))
            yield TabPane("qux4444", Label("qux contents"))

    def action_close_pane(self):
        tc = self.query_one(TabbedContent)
        if tc.active:
            tc.remove_pane(tc.active)


if __name__ == "__main__":
    app = ReproApp()
    app.run()
