from __future__ import annotations

import calendar
import datetime
from typing import Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.events import Mount
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import DataTable


class InvalidMonthNumber(Exception):
    pass


class InvalidWeekdayNumber(Exception):
    pass


class MonthCalendar(Widget):
    year: Reactive[int | None] = Reactive[Optional[int]](None)
    month: Reactive[int | None] = Reactive[Optional[int]](None)
    first_weekday: Reactive[int] = Reactive(0)
    show_cursor: Reactive[bool] = Reactive(True)

    def __init__(
        self,
        year: int | None = None,
        month: int | None = None,
        first_weekday: int = 0,
        show_cursor: bool = True,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.year = year
        self.month = month
        self.first_weekday = first_weekday
        self._calendar = calendar.Calendar(first_weekday)
        self.show_cursor = show_cursor

    def compose(self) -> ComposeResult:
        yield DataTable(
            show_cursor=self.show_cursor,
        )

    def previous_year(self) -> None:
        assert self.year is not None
        self.year -= 1

    def next_year(self) -> None:
        assert self.year is not None
        self.year += 1

    def previous_month(self) -> None:
        assert self.year is not None and self.month is not None
        if self.month == 1:
            self.year -= 1
            self.month = 12
        else:
            self.month -= 1

    def next_month(self) -> None:
        assert self.year is not None and self.month is not None
        if self.month == 12:
            self.year += 1
            self.month = 1
        else:
            self.month += 1

    def _on_mount(self, _: Mount) -> None:
        self._update_week_header()
        self._update_calendar_days()

    def _update_week_header(self) -> None:
        table = self.query_one(DataTable)
        day_names = calendar.day_abbr
        for day in self._calendar.iterweekdays():
            table.add_column(day_names[day])

    def _update_calendar_days(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for week in self.calendar_dates:
            table.add_row(*[self._format_day(date) for date in week])

    @property
    def calendar_dates(self) -> list[list[datetime.date]]:
        """
        A matrix of `datetime.date` objects for this month calendar. Each row
        represents a week, including dates before the start of the month
        or after the end of the month that are required to get a complete week.
        """
        assert self.year is not None and self.month is not None
        dates = list(self._calendar.itermonthdates(self.year, self.month))
        return [dates[i : i + 7] for i in range(0, len(dates), 7)]

    def _format_day(self, date: datetime.date) -> Text:
        formatted_day = Text(str(date.day), justify="center")
        if date.month != self.month:
            formatted_day.style = "grey37"
        return formatted_day

    def validate_year(self, year: int | None) -> int:
        if year is None:
            current_year = datetime.date.today().year
            return current_year
        return year

    def validate_month(self, month: int | None) -> int:
        if month is None:
            current_month = datetime.date.today().month
            return current_month
        if not 1 <= month <= 12:
            raise InvalidMonthNumber("Month number must be 1-12.")
        return month

    def validate_first_weekday(self, first_weekday: int) -> int:
        if not 0 <= first_weekday <= 6:
            raise InvalidWeekdayNumber(
                "Weekday number must be 0 (Monday) to 6 (Sunday)."
            )
        return first_weekday

    def watch_year(self) -> None:
        self.call_after_refresh(self._update_calendar_days)

    def watch_month(self) -> None:
        self.call_after_refresh(self._update_calendar_days)

    # def watch_first_weekday(self) -> None:
    #     self._calendar = calendar.Calendar(self.first_weekday)
    #     self._update_week_header()
    #     self._update_calendar_days()

    def watch_show_cursor(self, show_cursor: bool) -> None:
        table = self.query_one(DataTable)
        table.show_cursor = show_cursor
