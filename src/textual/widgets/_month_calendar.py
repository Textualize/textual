from __future__ import annotations

import calendar
import datetime
from typing import Sequence

from rich.text import Text

from .. import on
from ..app import ComposeResult
from ..binding import Binding
from ..coordinate import Coordinate
from ..events import Mount
from ..message import Message
from ..reactive import Reactive
from ..widget import Widget
from ..widgets import DataTable
from ..widgets.data_table import CellDoesNotExist


class InvalidWeekdayNumber(Exception):
    pass


class CalendarGrid(DataTable, inherit_bindings=False):
    # TODO: Ideally we want to hide that there's a DataTable underneath the
    # `MonthCalendar` widget. Is there any mechanism so component classes could be
    # defined in the parent and substitute the component styles in the child?
    # For example, allow styling the header using `.month-calendar--header`
    # rather than `.datatable--header`?
    DEFAULT_CSS = """
    CalendarGrid {
        height: auto;
        width: auto;

        .datatable--header {
            background: $surface;
        }
    }
    """


class MonthCalendar(Widget):
    BINDINGS = [
        Binding("enter", "select_date", "Select Date", show=False),
        Binding("up", "previous_week", "Previous Week", show=False),
        Binding("down", "next_week", "Next Week", show=False),
        Binding("right", "next_day", "Next Day", show=False),
        Binding("left", "previous_day", "Previous Day", show=False),
        Binding("pageup", "previous_month", "Previous Month", show=False),
        Binding("pagedown", "next_month", "Next month", show=False),
        Binding("ctrl+pageup", "previous_year", "Previous Year", show=False),
        Binding("ctrl+pagedown", "next_year", "Next Year", show=False),
    ]

    # TODO: min-width?
    DEFAULT_CSS = """
    MonthCalendar {
        height: auto;
        width: auto;
        min-height: 7;

        .month-calendar--outside-month {
            color: gray;
        }
    }
    """

    COMPONENT_CLASSES = {
        "month-calendar--outside-month",
    }

    date: Reactive[datetime.date] = Reactive(datetime.date.today)
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
        *,
        first_weekday: int = 0,
        show_cursor: bool = True,
        show_other_months: bool = True,
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
        yield CalendarGrid(show_cursor=self.show_cursor)

    @on(CalendarGrid.CellHighlighted)
    def _on_calendar_grid_cell_highlighted(
        self,
        event: CalendarGrid.CellHighlighted,
    ) -> None:
        event.stop()
        if not self.show_other_months and event.value is None:
            # TODO: This handling of blank cells is obviously a bit hacky.
            # Instead this widget should prevent highlighting a blank cell
            # altogether, either with the keyboard or mouse.
            calendar_grid = self.query_one(CalendarGrid)
            date_coordinate = self._get_date_coordinate(self.date)
            with self.prevent(CalendarGrid.CellHighlighted):
                calendar_grid.cursor_coordinate = date_coordinate
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
                self._update_calendar_grid(update_week_header=False)

            self.post_message(MonthCalendar.DateHighlighted(self, self.date))

    @on(CalendarGrid.CellSelected)
    def _on_calendar_grid_cell_selected(
        self,
        event: CalendarGrid.CellSelected,
    ) -> None:
        event.stop()
        if not self.show_other_months and event.value is None:
            calendar_grid = self.query_one(CalendarGrid)
            calendar_grid._show_hover_cursor = False
            return
        # We cannot rely on the `event.coordinate` for the selected date,
        # as selecting a date from the previous or next month will update the
        # calendar to bring that entire month into view and the date at this
        # co-ordinate will have changed! Thankfully it is safe to instead
        # simply use the calendar `date`, as clicking a table cell will emit a
        # `CellHighlighted` message *before* the `CellSelected` message.
        self.post_message(MonthCalendar.DateSelected(self, self.date))

    @on(CalendarGrid.HeaderSelected)
    def _on_calendar_grid_header_selected(
        self,
        event: CalendarGrid.HeaderSelected,
    ) -> None:
        event.stop()
        pass

    def previous_month(self) -> None:
        year = self.date.year
        month = self.date.month - 1
        if month < 1:
            year -= 1
            month += 12
        day = min(self.date.day, calendar.monthrange(year, month)[1])
        self.date = datetime.date(year, month, day)

    def next_month(self) -> None:
        year = self.date.year
        month = self.date.month + 1
        if month > 12:
            year += 1
            month -= 12
        day = min(self.date.day, calendar.monthrange(year, month)[1])
        self.date = datetime.date(year, month, day)

    def previous_year(self) -> None:
        year = self.date.year - 1
        month = self.date.month
        day = min(self.date.day, calendar.monthrange(year, month)[1])
        self.date = datetime.date(year, month, day)

    def next_year(self) -> None:
        year = self.date.year + 1
        month = self.date.month
        day = min(self.date.day, calendar.monthrange(year, month)[1])
        self.date = datetime.date(year, month, day)

    def _on_mount(self, _: Mount) -> None:
        self._update_calendar_grid(update_week_header=True)

        def hide_hover_cursor_if_blank_cell(hover_coordinate: Coordinate) -> None:
            calendar_grid = self.query_one(CalendarGrid)
            try:
                hover_cell_value = calendar_grid.get_cell_at(hover_coordinate)
            except CellDoesNotExist:
                calendar_grid._set_hover_cursor(False)
                return
            if hover_cell_value is None:
                calendar_grid._set_hover_cursor(False)

        self.watch(
            self.query_one(CalendarGrid),
            "hover_coordinate",
            hide_hover_cursor_if_blank_cell,
        )

    def _update_calendar_grid(self, update_week_header: bool) -> None:
        calendar_grid = self.query_one(CalendarGrid)
        old_hover_coordinate = calendar_grid.hover_coordinate
        calendar_grid.clear()

        if update_week_header:
            old_columns = calendar_grid.columns.copy()
            for old_column in old_columns:
                calendar_grid.remove_column(old_column)

            day_names = calendar.day_abbr
            for day in self._calendar.iterweekdays():
                calendar_grid.add_column(day_names[day])

        with self.prevent(CalendarGrid.CellHighlighted):
            for week in self._calendar_dates:
                calendar_grid.add_row(
                    *[
                        self._format_day(date) if date is not None else None
                        for date in week
                    ]
                )

        date_coordinate = self._get_date_coordinate(self.date)
        calendar_grid.cursor_coordinate = date_coordinate

        calendar_grid.hover_coordinate = old_hover_coordinate

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

        calendar_dates = [list(week) for week in month_weeks]

        if len(calendar_dates) < 6:
            previous_month_weeks = self._get_previous_month_weeks()
            next_month_weeks = self._get_next_month_weeks()

            current_first_date = calendar_dates[0][0]
            assert isinstance(current_first_date, datetime.date)
            current_last_date = calendar_dates[-1][6]
            assert isinstance(current_last_date, datetime.date)

            if len(calendar_dates) == 4:
                calendar_dates = (
                    [previous_month_weeks[-1]] + calendar_dates + [next_month_weeks[0]]
                )
            elif current_first_date.day == 1:
                calendar_dates = [previous_month_weeks[-1]] + calendar_dates
            elif current_last_date.month == self.date.month:
                calendar_dates = calendar_dates + [next_month_weeks[0]]
            else:
                calendar_dates = calendar_dates + [next_month_weeks[1]]

        assert len(calendar_dates) == 6

        return calendar_dates

    def _get_previous_month_weeks(self) -> list[list[datetime.date]]:
        previous_month = self.date.month - 1
        previous_month_year = self.date.year
        if previous_month < 1:
            previous_month_year -= 1
            previous_month += 12
        return self._calendar.monthdatescalendar(previous_month_year, previous_month)

    def _get_next_month_weeks(self) -> list[list[datetime.date]]:
        next_month = self.date.month + 1
        next_month_year = self.date.year
        if next_month > 12:
            next_month_year += 1
            next_month -= 12
        return self._calendar.monthdatescalendar(next_month_year, next_month)

    def _get_date_coordinate(self, date: datetime.date) -> Coordinate:
        for week_index, week in enumerate(self._calendar_dates):
            if date in week:
                return Coordinate(week_index, week.index(date))

        raise ValueError("Date is out of range for this month calendar.")

    def _format_day(self, date: datetime.date) -> Text:
        formatted_day = Text(str(date.day), justify="center")
        if date.month != self.date.month:
            outside_month_style = self.get_component_rich_style(
                "month-calendar--outside-month", partial=True
            )
            formatted_day.stylize(outside_month_style)
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
            self._update_calendar_grid(update_week_header=False)
        else:
            calendar_grid = self.query_one(CalendarGrid)
            cursor_row, cursor_column = calendar_grid.cursor_coordinate
            if self._calendar_dates[cursor_row][cursor_column] != new_date:
                date_coordinate = self._get_date_coordinate(self.date)
                calendar_grid.cursor_coordinate = date_coordinate

    def watch_first_weekday(self) -> None:
        self._calendar = calendar.Calendar(self.first_weekday)
        self._calendar_dates = self._get_calendar_dates()
        if not self.is_mounted:
            return
        self._update_calendar_grid(update_week_header=True)

    def watch_show_cursor(self, show_cursor: bool) -> None:
        if not self.is_mounted:
            return
        calendar_grid = self.query_one(CalendarGrid)
        calendar_grid.show_cursor = show_cursor

    def watch_show_other_months(self) -> None:
        self._calendar_dates = self._get_calendar_dates()
        if not self.is_mounted:
            return
        self._update_calendar_grid(update_week_header=False)

    def action_select_date(self) -> None:
        calendar_grid = self.query_one(CalendarGrid)
        calendar_grid.action_select_cursor()

    def action_previous_day(self) -> None:
        self.date -= datetime.timedelta(days=1)

    def action_next_day(self) -> None:
        self.date += datetime.timedelta(days=1)

    def action_previous_week(self) -> None:
        self.date -= datetime.timedelta(weeks=1)

    def action_next_week(self) -> None:
        self.date += datetime.timedelta(weeks=1)

    def action_previous_month(self) -> None:
        self.previous_month()

    def action_next_month(self) -> None:
        self.next_month()

    def action_previous_year(self) -> None:
        self.previous_year()

    def action_next_year(self) -> None:
        self.next_year()
