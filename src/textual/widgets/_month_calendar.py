from __future__ import annotations

import calendar
import datetime
from typing import Optional

from rich.text import Text

from textual import on
from textual.app import ComposeResult
from textual.coordinate import Coordinate
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
    cursor_date: Reactive[datetime.date | None] = Reactive[Optional[datetime.date]](
        None
    )

    def __init__(
        self,
        year: int | None = None,
        month: int | None = None,
        first_weekday: int = 0,
        show_cursor: bool = True,
        cursor_date: datetime.date | None = None,
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
        self.cursor_date = cursor_date

    def compose(self) -> ComposeResult:
        yield DataTable(
            show_cursor=self.show_cursor,
        )

    @on(DataTable.CellHighlighted)
    def _on_datatable_cell_highlighted(
        self,
        event: DataTable.CellHighlighted,
    ) -> None:
        event.stop()
        row, column = event.coordinate
        self.cursor_date = self.calendar_dates[row][column]

    @property
    def is_current_month(self) -> bool:
        today = datetime.date.today()
        return self.year == today.year and self.month == today.month

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

    def move_cursor(self, date: datetime.date) -> None:
        date_coordinate = self.get_date_coordinate(date)
        table = self.query_one(DataTable)
        table.cursor_coordinate = date_coordinate

    def _on_mount(self, _: Mount) -> None:
        self._update_week_header()
        self._update_calendar_days()
        if self.show_cursor:
            assert self.cursor_date is not None
            self.move_cursor(self.cursor_date)

    def _update_week_header(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        old_columns = table.columns.copy()
        for old_column in old_columns:
            table.remove_column(old_column)

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

    def get_date_coordinate(self, date: datetime.date) -> Coordinate:
        for week_index, week in enumerate(self.calendar_dates):
            try:
                return Coordinate(week_index, week.index(date))
            except ValueError:
                pass
        raise ValueError("Date is out of range for this month calendar.")

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

    def validate_cursor_date(
        self,
        cursor_date: datetime.date | None,
    ) -> datetime.date | None:
        if self.show_cursor is None:
            return None
        assert self.year is not None and self.month is not None
        if cursor_date is None:
            if self.is_current_month:
                return datetime.date.today()
            else:
                return datetime.date(self.year, self.month, 1)
        return cursor_date

    def watch_year(self) -> None:
        if not self.is_mounted:
            return
        self._update_calendar_days()

    def watch_month(self) -> None:
        if not self.is_mounted:
            return
        self._update_calendar_days()

    def watch_first_weekday(self) -> None:
        self._calendar = calendar.Calendar(self.first_weekday)
        if not self.is_mounted:
            return
        self._update_week_header()
        self._update_calendar_days()

    def watch_show_cursor(self, show_cursor: bool) -> None:
        if not self.is_mounted:
            return
        table = self.query_one(DataTable)
        table.show_cursor = show_cursor

    def watch_cursor_date(self, cursor_date: datetime.date | None) -> None:
        if not self.is_mounted or cursor_date is None:
            return
        with self.prevent(DataTable.CellHighlighted):
            self.move_cursor(cursor_date)
