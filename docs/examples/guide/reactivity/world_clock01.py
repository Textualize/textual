from datetime import datetime

from pytz import timezone

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Digits, Label


class WorldClock(Widget):

    time: reactive[datetime] = reactive(datetime.now)

    def __init__(self, timezone: str) -> None:
        self.timezone = timezone
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.timezone)
        yield Digits()

    def watch_time(self, time: datetime) -> None:
        localized_time = time.astimezone(timezone(self.timezone))
        self.query_one(Digits).update(localized_time.strftime("%H:%M:%S"))


class WorldClockApp(App):
    CSS_PATH = "world_clock01.tcss"

    time: reactive[datetime] = reactive(datetime.now)

    def compose(self) -> ComposeResult:
        yield WorldClock("Europe/London")
        yield WorldClock("Europe/Paris")
        yield WorldClock("Asia/Tokyo")

    def update_time(self) -> None:
        self.time = datetime.now()

    def watch_time(self, time: datetime) -> None:
        for world_clock in self.query(WorldClock):  # (1)!
            world_clock.time = time

    def on_mount(self) -> None:
        self.update_time()
        self.set_interval(1, self.update_time)


if __name__ == "__main__":
    app = WorldClockApp()
    app.run()
