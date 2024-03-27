from datetime import datetime

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Digits


class Clock(App):

    CSS = """
    Screen {align: center middle}
    Digits {width: auto}
    """

    time: reactive[datetime] = reactive(datetime.now, recompose=True)

    def compose(self) -> ComposeResult:
        yield Digits(f"{self.time:%X}")

    def update_time(self) -> None:
        self.time = datetime.now()

    def on_mount(self) -> None:
        self.set_interval(1, self.update_time)


if __name__ == "__main__":
    app = Clock()
    app.run()
