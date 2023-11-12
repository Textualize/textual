from textual.app import App, ComposeResult
from textual.widgets import MonthCalendar


class MonthCalendarApp(App):
    def compose(self) -> ComposeResult:
        yield MonthCalendar(year=2021, month=6)


if __name__ == "__main__":
    app = MonthCalendarApp()
    app.run()
