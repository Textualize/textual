from textual import layout, events
from textual.app import App, ComposeResult
from textual.widgets import Button


class ButtonsApp(App[str]):
    def compose(self) -> ComposeResult:
        yield layout.Vertical(
            Button("default", id="foo"),
            Button.success("success", id="bar"),
            Button.warning("warning", id="baz"),
            Button.error("error", id="baz"),
        )

    def handle_pressed(self, event: Button.Pressed) -> None:
        self.app.bell()
        print("pressed", event.button.id)

    async def on_key(self, event: events.Key) -> None:
        await self.dispatch_key(event)

    def key_a(self):
        print(f"text-success: {self.stylesheet.variables.get('text-success')}")
        print(
            f"text-success-darken-1: {self.stylesheet.variables.get('text-success-darken-1')}"
        )
        self.dark = not self.dark


app = ButtonsApp(
    log_path="textual.log", css_path="buttons.css", watch_css=True, log_verbosity=2
)

if __name__ == "__main__":
    result = app.run()
    print(repr(result))
