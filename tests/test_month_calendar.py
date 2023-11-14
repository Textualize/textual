import datetime

import pytest
from textual.app import App, ComposeResult
from textual.coordinate import Coordinate
from textual.widgets import DataTable, MonthCalendar
from textual.widgets.month_calendar import InvalidMonthNumber, InvalidWeekdayNumber


def test_year_defaults_to_current_year_if_none_provided():
    month_calendar = MonthCalendar()
    current_year = datetime.date.today().year
    assert month_calendar.year == current_year


def test_month_defaults_to_current_month_if_none_provided():
    month_calendar = MonthCalendar()
    current_month = datetime.date.today().month
    assert month_calendar.month == current_month


def test_invalid_month_number_raises_exception():
    with pytest.raises(InvalidMonthNumber):
        month_calendar = MonthCalendar(month=13)


def test_invalid_weekday_number_raises_exception():
    with pytest.raises(InvalidWeekdayNumber):
        month_calendar = MonthCalendar(first_weekday=7)


def test_calendar_dates_property():
    month_calendar = MonthCalendar(year=2021, month=6)
    first_monday = datetime.date(2021, 5, 31)
    expected_date = first_monday
    for week in range(len(month_calendar.calendar_dates)):
        for day in range(0, 7):
            assert month_calendar.calendar_dates[week][day] == expected_date
            expected_date += datetime.timedelta(days=1)


class MonthCalendarApp(App):
    def compose(self) -> ComposeResult:
        yield MonthCalendar(year=2021, month=6)


async def test_calendar_table_week_header():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        table = month_calendar.query_one(DataTable)
        actual_labels = [col.label.plain for col in table.columns.values()]
        expected_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        assert actual_labels == expected_labels


async def test_calendar_table_days():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        table = month_calendar.query_one(DataTable)
        for row, week in enumerate(month_calendar.calendar_dates):
            for column, date in enumerate(week):
                actual_day = table.get_cell_at(Coordinate(row, column)).plain
                expected_day = str(date.day)
                assert actual_day == expected_day


# async def test_calendar_table_after_reactive_year_change():
#     pass
#
#
# async def test_calendar_table_after_reactive_month_change():
#     pass
