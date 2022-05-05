from textual.app import App, ComposeResult

from textual.widgets import Button
from textual import layout


class ButtonsApp(App[str]):
    def compose(self) -> ComposeResult:
        yield layout.Vertical(
            Button("foo", id="foo"),
            Button("bar", id="bar"),
            Button("baz", id="baz"),
        )

    def handle_pressed(self, event: Button.Pressed) -> None:
        self.app.bell()
        self.log("pressed", event.button.id)
        self.exit(event.button.id)


app = ButtonsApp(log_path="textual.log", log_verbosity=2)

if __name__ == "__main__":
    result = app.run()
    print(repr(result))
