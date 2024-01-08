from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, ProgressBar


class Counter(Widget):
    DEFAULT_CSS = "Counter { height: auto; }"
    counter = reactive(0)  # (1)!

    def compose(self) -> ComposeResult:
        yield Label()
        yield Button("+10")

    def on_button_pressed(self) -> None:
        self.counter += 10

    def watch_counter(self, counter_value: int):
        self.query_one(Label).update(str(counter_value))


class WatchApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Counter()
        yield ProgressBar(total=100, show_eta=False)

    def on_mount(self):
        def update_progress(counter_value: int):  # (2)!
            self.query_one(ProgressBar).update(progress=counter_value)

        self.watch(self.query_one(Counter), "counter", update_progress)  # (3)!


if __name__ == "__main__":
    WatchApp().run()
