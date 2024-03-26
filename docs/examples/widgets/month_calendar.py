import datetime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import MonthCalendar


class MonthCalendarApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    """

    BINDINGS = [
        Binding("pageup", "next_month", priority=True),
        Binding("pagedown", "previous_month", priority=True),
        Binding("ctrl+pageup", "next_year", priority=True),
        Binding("ctrl+pagedown", "previous_year", priority=True),
        Binding("ctrl+s", "toggle_show_other_months"),
    ]

    def compose(self) -> ComposeResult:
        yield MonthCalendar(datetime.date(year=2021, month=6, day=3))

    def action_next_month(self) -> None:
        self.query_one(MonthCalendar).next_month()

    def action_previous_month(self) -> None:
        self.query_one(MonthCalendar).previous_month()

    def action_next_year(self) -> None:
        self.query_one(MonthCalendar).next_year()

    def action_previous_year(self) -> None:
        self.query_one(MonthCalendar).previous_year()

    def action_toggle_show_other_months(self) -> None:
        calendar = self.query_one(MonthCalendar)
        calendar.show_other_months = not calendar.show_other_months


if __name__ == "__main__":
    app = MonthCalendarApp()
    app.run()
