from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Input, Label


class MultiGreet(App):
    names: reactive[list[str]] = reactive(list, recompose=True)  # (1)!

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Give me a name")
        for name in self.names:
            yield Label(f"Hello, {name}")

    def on_input_submitted(self, event: Input.Changed) -> None:
        self.names.append(event.value)
        self.mutate_reactive(MultiGreet.names)  # (2)!


if __name__ == "__main__":
    app = MultiGreet()
    app.run()
