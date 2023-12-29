from __future__ import annotations

import calendar
import datetime

from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]
from rich.text import Text

from textual import on
from textual.app import ComposeResult
from textual.coordinate import Coordinate
from textual.events import Mount
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import DataTable


class InvalidWeekdayNumber(Exception):
    pass


class MonthCalendar(Widget):
    # TODO: min-width?
    DEFAULT_CSS = """
    MonthCalendar {
        height: auto;
        width: auto;
        min-height: 7;
    }

    MonthCalendar > DataTable {
        height: auto;
        width: auto;
    }
    """

    date: Reactive[datetime.date] = Reactive(datetime.date.today())
    first_weekday: Reactive[int] = Reactive(0)
    show_cursor: Reactive[bool] = Reactive(True)

    def __init__(
        self,
        date: datetime.date = datetime.date.today(),
        first_weekday: int = 0,
        show_cursor: bool = True,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.date = date
        self.first_weekday = first_weekday
        self._calendar = calendar.Calendar(first_weekday)
        self.show_cursor = show_cursor

    def compose(self) -> ComposeResult:
        yield DataTable(show_cursor=self.show_cursor)

    @on(DataTable.CellHighlighted)
    def _on_datatable_cell_highlighted(
        self,
        event: DataTable.CellHighlighted,
    ) -> None:
        event.stop()
        row, column = event.coordinate
        self.date = self.calendar_dates[row][column]

    def previous_year(self) -> None:
        self.date -= relativedelta(years=1)

    def next_year(self) -> None:
        self.date += relativedelta(years=1)

    def previous_month(self) -> None:
        self.date -= relativedelta(months=1)

    def next_month(self) -> None:
        self.date += relativedelta(months=1)

    def _on_mount(self, _: Mount) -> None:
        self._update_week_header()
        self._update_calendar_days()

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
        with self.prevent(DataTable.CellHighlighted):
            for week in self.calendar_dates:
                table.add_row(*[self._format_day(date) for date in week])

            date_coordinate = self._get_date_coordinate(self.date)
            table.cursor_coordinate = date_coordinate

    @property
    def calendar_dates(self) -> list[list[datetime.date]]:
        """
        A matrix of `datetime.date` objects for this month calendar. Each row
        represents a week, including dates before the start of the month
        or after the end of the month that are required to get a complete week.
        """
        dates = list(self._calendar.itermonthdates(self.date.year, self.date.month))
        return [dates[i : i + 7] for i in range(0, len(dates), 7)]

    def _get_date_coordinate(self, date: datetime.date) -> Coordinate:
        for week_index, week in enumerate(self.calendar_dates):
            try:
                return Coordinate(week_index, week.index(date))
            except ValueError:
                pass
        raise ValueError("Date is out of range for this month calendar.")

    def _format_day(self, date: datetime.date) -> Text:
        formatted_day = Text(str(date.day), justify="center")
        if date.month != self.date.month:
            formatted_day.style = "grey37"
        return formatted_day

    def validate_first_weekday(self, first_weekday: int) -> int:
        if not 0 <= first_weekday <= 6:
            raise InvalidWeekdayNumber(
                "Weekday number must be 0 (Monday) to 6 (Sunday)."
            )
        return first_weekday

    def watch_date(self) -> None:
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
