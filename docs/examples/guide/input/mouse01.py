from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import RichLog, Static


class PlayArea(Container):
    def on_mount(self) -> None:
        self.capture_mouse()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        self.screen.query_one(RichLog).write(event)
        self.query_one(Ball).offset = event.offset - (8, 2)


class Ball(Static):
    pass


class MouseApp(App):
    CSS_PATH = "mouse01.tcss"

    def compose(self) -> ComposeResult:
        yield RichLog()
        yield PlayArea(Ball("Textual"))


if __name__ == "__main__":
    app = MouseApp()
    app.run()
