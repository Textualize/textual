from __future__ import annotations

import calendar
import datetime

from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]
from rich.text import Text

from textual import on
from textual.app import ComposeResult
from textual.coordinate import Coordinate
from textual.events import Mount
from textual.message import Message
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
    show_other_months: Reactive[bool] = Reactive(True)

    class DateSelected(Message):
        def __init__(
            self,
            month_calendar: MonthCalendar,
            value: datetime.date,
        ) -> None:
            super().__init__()
            self.month_calendar: MonthCalendar = month_calendar
            self.value: datetime.date = value

        @property
        def control(self) -> MonthCalendar:
            return self.month_calendar

    def __init__(
        self,
        date: datetime.date = datetime.date.today(),
        first_weekday: int = 0,
        show_cursor: bool = True,
        show_other_months: bool = True,
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
        self.show_other_months = show_other_months

    def compose(self) -> ComposeResult:
        yield DataTable(show_cursor=self.show_cursor)

    @on(DataTable.CellHighlighted)
    def _on_datatable_cell_highlighted(
        self,
        event: DataTable.CellHighlighted,
    ) -> None:
        event.stop()
        if not self.show_other_months and event.value is None:
            table = self.query_one(DataTable)
            date_coordinate = self._get_date_coordinate(self.date)
            table.cursor_coordinate = date_coordinate
        else:
            row, column = event.coordinate
            highlighted_date = self._calendar_dates[row][column]
            assert isinstance(highlighted_date, datetime.date)
            self.date = highlighted_date

    @on(DataTable.CellSelected)
    def _on_datatable_cell_selected(
        self,
        event: DataTable.CellSelected,
    ) -> None:
        event.stop()
        # We cannot rely on the `event.coordinate` for the selected date,
        # as selecting a date from the previous or next month will update the
        # calendar to bring that entire month into view and the date at this
        # co-ordinate will have changed! Thankfully it is safe to instead
        # simply use the calendar `date`, as clicking a table cell will emit a
        # `CellHighlighted` message *before* the `CellSelected` message.
        self.post_message(MonthCalendar.DateSelected(self, self.date))

    def previous_year(self) -> None:
        self.date -= relativedelta(years=1)

    def next_year(self) -> None:
        self.date += relativedelta(years=1)

    def previous_month(self) -> None:
        self.date -= relativedelta(months=1)

    def next_month(self) -> None:
        self.date += relativedelta(months=1)

    def _on_mount(self, _: Mount) -> None:
        self._update_calendar_table(update_week_header=True)

    def _update_calendar_table(self, update_week_header: bool) -> None:
        table = self.query_one(DataTable)
        old_hover_coordinate = table.hover_coordinate
        table.clear()

        if update_week_header:
            old_columns = table.columns.copy()
            for old_column in old_columns:
                table.remove_column(old_column)

            day_names = calendar.day_abbr
            for day in self._calendar.iterweekdays():
                table.add_column(day_names[day])

        with self.prevent(DataTable.CellHighlighted):
            for week in self._calendar_dates:
                table.add_row(
                    *[
                        self._format_day(date) if date is not None else None
                        for date in week
                    ]
                )

            date_coordinate = self._get_date_coordinate(self.date)
            table.cursor_coordinate = date_coordinate

        table.hover_coordinate = old_hover_coordinate

    @property
    def _calendar_dates(self) -> list[list[datetime.date | None]]:
        """A matrix of `datetime.date` objects for this month calendar, where
        each row represents a week. If `show_other_months` is True this includes
        dates from the previous and next month that are required to get a
        complete week, otherwise these days are 'None'
        """
        complete_dates = self._calendar.itermonthdates(self.date.year, self.date.month)
        calendar_dates: list[datetime.date | None]
        if not self.show_other_months:
            calendar_dates = [
                date if date.month == self.date.month else None
                for date in complete_dates
            ]
        else:
            calendar_dates = list(complete_dates)

        return [calendar_dates[i : i + 7] for i in range(0, len(calendar_dates), 7)]

    def _get_date_coordinate(self, date: datetime.date) -> Coordinate:
        for week_index, week in enumerate(self._calendar_dates):
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

    def watch_date(self, old_date: datetime.date, new_date: datetime.date) -> None:
        if not self.is_mounted:
            return
        if (new_date.month != old_date.month) or (new_date.year != old_date.year):
            self._update_calendar_table(update_week_header=False)
        else:
            table = self.query_one(DataTable)
            date_coordinate = self._get_date_coordinate(self.date)
            table.cursor_coordinate = date_coordinate

    def watch_first_weekday(self) -> None:
        self._calendar = calendar.Calendar(self.first_weekday)
        if not self.is_mounted:
            return
        self._update_calendar_table(update_week_header=True)

    def watch_show_cursor(self, show_cursor: bool) -> None:
        if not self.is_mounted:
            return
        table = self.query_one(DataTable)
        table.show_cursor = show_cursor

    def watch_show_other_months(self) -> None:
        if not self.is_mounted:
            return
        self._update_calendar_table(update_week_header=False)
