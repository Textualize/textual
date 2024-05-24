from __future__ import annotations

import calendar
import datetime
from typing import Sequence

# TODO: Does `python-dateutil` need adding as a dependency?
from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]
from rich.text import Text

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.coordinate import Coordinate
from textual.events import Mount
from textual.message import Message
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import DataTable
from textual.widgets.data_table import CellDoesNotExist


class InvalidWeekdayNumber(Exception):
    pass


class MonthCalendarTable(DataTable, inherit_bindings=False):
    pass


class MonthCalendar(Widget):
    BINDINGS = [
        Binding("enter", "select_date", "Select Date", show=False),
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
        Binding("right", "cursor_right", "Cursor Right", show=False),
        Binding("left", "cursor_left", "Cursor Left", show=False),
        Binding("pageup", "next_month", "Next month", show=False),
        Binding("pagedown", "previous_month", "Previous Month", show=False),
        Binding("ctrl+pageup", "next_year", "Next Year", show=False),
        Binding("ctrl+pagedown", "previous_year", "Previous Year", show=False),
    ]

    # TODO: min-width?
    DEFAULT_CSS = """
    MonthCalendar {
        height: auto;
        width: auto;
        min-height: 7;
    }

    MonthCalendar > MonthCalendarTable {
        height: auto;
        width: auto;
    }
    """

    date: Reactive[datetime.date] = Reactive(datetime.date.today())
    first_weekday: Reactive[int] = Reactive(0)
    show_cursor: Reactive[bool] = Reactive(True)
    show_other_months: Reactive[bool] = Reactive(True)

    class DateHighlighted(Message):
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
        self._calendar_dates = self._get_calendar_dates()

    def compose(self) -> ComposeResult:
        yield MonthCalendarTable(show_cursor=self.show_cursor)

    @on(MonthCalendarTable.CellHighlighted)
    def _on_table_cell_highlighted(
        self,
        event: MonthCalendarTable.CellHighlighted,
    ) -> None:
        event.stop()
        if not self.show_other_months and event.value is None:
            table = self.query_one(MonthCalendarTable)
            date_coordinate = self._get_date_coordinate(self.date)
            with self.prevent(MonthCalendarTable.CellHighlighted):
                table.cursor_coordinate = date_coordinate
        else:
            cursor_row, cursor_column = event.coordinate
            new_date = self._calendar_dates[cursor_row][cursor_column]
            assert isinstance(new_date, datetime.date)
            # Avoid possible race condition by setting the `date` reactive
            # without invoking the watcher. When mashing the arrow keys, this
            # otherwise would cause the app to lag or freeze entirely.
            old_date = self.date
            self.set_reactive(MonthCalendar.date, new_date)
            if (new_date.month != old_date.month) or (new_date.year != old_date.year):
                self._calendar_dates = self._get_calendar_dates()
                self._update_calendar_table(update_week_header=False)

            self.post_message(MonthCalendar.DateHighlighted(self, self.date))

    @on(MonthCalendarTable.CellSelected)
    def _on_table_cell_selected(
        self,
        event: MonthCalendarTable.CellSelected,
    ) -> None:
        event.stop()
        if not self.show_other_months and event.value is None:
            table = self.query_one(MonthCalendarTable)
            table._show_hover_cursor = False
            return
        # We cannot rely on the `event.coordinate` for the selected date,
        # as selecting a date from the previous or next month will update the
        # calendar to bring that entire month into view and the date at this
        # co-ordinate will have changed! Thankfully it is safe to instead
        # simply use the calendar `date`, as clicking a table cell will emit a
        # `CellHighlighted` message *before* the `CellSelected` message.
        self.post_message(MonthCalendar.DateSelected(self, self.date))

    @on(MonthCalendarTable.HeaderSelected)
    def _on_table_header_selected(
        self,
        event: MonthCalendarTable.HeaderSelected,
    ) -> None:
        event.stop()
        pass

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

        def hide_hover_cursor_if_blank_cell(hover_coordinate: Coordinate) -> None:
            table = self.query_one(MonthCalendarTable)
            try:
                hover_cell_value = table.get_cell_at(hover_coordinate)
            except CellDoesNotExist:
                table._set_hover_cursor(False)
                return
            if hover_cell_value is None:
                table._set_hover_cursor(False)

        self.watch(
            self.query_one(MonthCalendarTable),
            "hover_coordinate",
            hide_hover_cursor_if_blank_cell,
        )

    def _update_calendar_table(self, update_week_header: bool) -> None:
        table = self.query_one(MonthCalendarTable)
        old_hover_coordinate = table.hover_coordinate
        table.clear()

        if update_week_header:
            old_columns = table.columns.copy()
            for old_column in old_columns:
                table.remove_column(old_column)

            day_names = calendar.day_abbr
            for day in self._calendar.iterweekdays():
                table.add_column(day_names[day])

        with self.prevent(MonthCalendarTable.CellHighlighted):
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

    def _get_calendar_dates(self) -> list[Sequence[datetime.date | None]]:
        """A matrix of `datetime.date` objects for this month calendar, where
        each row represents a week. If `show_other_months` is True, this returns
        a six-week calendar including dates from the previous and next month.
        If `show_other_months` is False, only weeks required for the month are
        included and any dates outside the month are 'None'.
        """
        month_weeks = self._calendar.monthdatescalendar(self.date.year, self.date.month)
        calendar_dates: list[Sequence[datetime.date | None]]
        if not self.show_other_months:
            calendar_dates = [
                [date if date.month == self.date.month else None for date in week]
                for week in month_weeks
            ]
            return calendar_dates

        calendar_dates = [[date for date in week] for week in month_weeks]
        if len(calendar_dates) < 6:
            prev_month = self.date - relativedelta(months=1)
            prev_month_weeks = self._calendar.monthdatescalendar(
                prev_month.year, prev_month.month
            )

            next_month = self.date + relativedelta(months=1)
            next_month_weeks = self._calendar.monthdatescalendar(
                next_month.year, next_month.month
            )

            curr_first_date = calendar_dates[0][0]
            assert isinstance(curr_first_date, datetime.date)

            if len(calendar_dates) == 4:  # special case for February
                calendar_dates = (
                    [prev_month_weeks[-1]] + calendar_dates + [next_month_weeks[0]]
                )
            elif curr_first_date.day == 1:
                calendar_dates = [prev_month_weeks[-1]] + calendar_dates
            else:
                curr_last_date = calendar_dates[-1][6]
                assert isinstance(curr_last_date, datetime.date)
                if curr_last_date.month == self.date.month:
                    calendar_dates = calendar_dates + [next_month_weeks[0]]
                else:
                    calendar_dates = calendar_dates + [next_month_weeks[1]]

        assert len(calendar_dates) == 6

        return calendar_dates

    def _get_date_coordinate(self, date: datetime.date) -> Coordinate:
        for week_index, week in enumerate(self._calendar_dates):
            if date in week:
                return Coordinate(week_index, week.index(date))

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
            self._calendar_dates = self._get_calendar_dates()
            self._update_calendar_table(update_week_header=False)
        else:
            table = self.query_one(MonthCalendarTable)
            cursor_row, cursor_column = table.cursor_coordinate
            if self._calendar_dates[cursor_row][cursor_column] != new_date:
                date_coordinate = self._get_date_coordinate(self.date)
                table.cursor_coordinate = date_coordinate

    def watch_first_weekday(self) -> None:
        self._calendar = calendar.Calendar(self.first_weekday)
        self._calendar_dates = self._get_calendar_dates()
        if not self.is_mounted:
            return
        self._update_calendar_table(update_week_header=True)

    def watch_show_cursor(self, show_cursor: bool) -> None:
        if not self.is_mounted:
            return
        table = self.query_one(MonthCalendarTable)
        table.show_cursor = show_cursor

    def watch_show_other_months(self) -> None:
        self._calendar_dates = self._get_calendar_dates()
        if not self.is_mounted:
            return
        self._update_calendar_table(update_week_header=False)

    def action_select_date(self) -> None:
        table = self.query_one(MonthCalendarTable)
        table.action_select_cursor()

    def action_cursor_up(self) -> None:
        table = self.query_one(MonthCalendarTable)
        table.action_cursor_up()

    def action_cursor_down(self) -> None:
        table = self.query_one(MonthCalendarTable)
        table.action_cursor_down()

    def action_cursor_right(self) -> None:
        table = self.query_one(MonthCalendarTable)
        table.action_cursor_right()

    def action_cursor_left(self) -> None:
        table = self.query_one(MonthCalendarTable)
        table.action_cursor_left()

    def action_next_month(self) -> None:
        self.next_month()

    def action_previous_month(self) -> None:
        self.previous_month()

    def action_next_year(self) -> None:
        self.next_year()

    def action_previous_year(self) -> None:
        self.previous_year()
