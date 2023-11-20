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


def test_get_date_coordinate():
    month_calendar = MonthCalendar(year=2021, month=6)
    expected_coordinate = Coordinate(0, 3)
    actual_coordinate = month_calendar.get_date_coordinate(
        datetime.date(2021, 6, 3),
    )
    assert actual_coordinate == expected_coordinate


def test_get_date_coordinate_when_out_of_range():
    month_calendar = MonthCalendar(year=2021, month=6)
    with pytest.raises(ValueError):
        month_calendar.get_date_coordinate(datetime.date(2021, 1, 1))


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


async def test_calendar_table_after_reactive_year_change():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        month_calendar.year = 2023
        table = month_calendar.query_one(DataTable)
        expected_first_monday = datetime.date(2023, 5, 29)
        actual_first_monday = month_calendar.calendar_dates[0][0]
        assert actual_first_monday == expected_first_monday
        assert table.get_cell_at(Coordinate(0, 0)).plain == "29"


async def test_calendar_table_after_reactive_month_change():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        month_calendar.month = 7
        table = month_calendar.query_one(DataTable)
        expected_first_monday = datetime.date(2021, 6, 28)
        actual_first_monday = month_calendar.calendar_dates[0][0]
        assert actual_first_monday == expected_first_monday
        assert table.get_cell_at(Coordinate(0, 0)).plain == "28"


# async def test_calendar_table_after_reactive_first_weekday_change():
#     app = MonthCalendarApp()
#     async with app.run_test() as pilot:
#         month_calendar = pilot.app.query_one(MonthCalendar)
#         month_calendar.first_weekday = 6  # Sunday
#         table = month_calendar.query_one(DataTable)
#
#         actual_labels = [col.label.plain for col in table.columns.values()]
#         expected_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
#         assert actual_labels == expected_labels
#
#         expected_first_sunday = datetime.date(2021, 5, 30)
#         actual_first_sunday = month_calendar.calendar_dates[0][0]
#         assert actual_first_sunday == expected_first_sunday
#         assert table.get_cell_at(Coordinate(0, 0)).plain == "30"


async def test_show_cursor():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        table = month_calendar.query_one(DataTable)
        assert table.show_cursor is True
        month_calendar.show_cursor = False
        assert table.show_cursor is False


async def test_previous_year():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        month_calendar.previous_year()
        table = month_calendar.query_one(DataTable)
        expected_first_monday = datetime.date(2020, 6, 1)
        actual_first_monday = month_calendar.calendar_dates[0][0]
        assert actual_first_monday == expected_first_monday
        assert table.get_cell_at(Coordinate(0, 0)).plain == "1"


async def test_next_year():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        month_calendar.next_year()
        table = month_calendar.query_one(DataTable)
        expected_first_monday = datetime.date(2022, 5, 30)
        actual_first_monday = month_calendar.calendar_dates[0][0]
        assert actual_first_monday == expected_first_monday
        assert table.get_cell_at(Coordinate(0, 0)).plain == "30"


async def test_previous_month():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        month_calendar.previous_month()
        table = month_calendar.query_one(DataTable)
        expected_first_monday = datetime.date(2021, 4, 26)
        actual_first_monday = month_calendar.calendar_dates[0][0]
        assert actual_first_monday == expected_first_monday
        assert table.get_cell_at(Coordinate(0, 0)).plain == "26"


async def test_previous_month_when_month_is_january():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        month_calendar.month = 1
        month_calendar.previous_month()
        table = month_calendar.query_one(DataTable)
        expected_first_monday = datetime.date(2020, 11, 30)
        actual_first_monday = month_calendar.calendar_dates[0][0]
        assert actual_first_monday == expected_first_monday
        assert table.get_cell_at(Coordinate(0, 0)).plain == "30"


async def test_next_month():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        month_calendar.next_month()
        table = month_calendar.query_one(DataTable)
        expected_first_monday = datetime.date(2021, 6, 28)
        actual_first_monday = month_calendar.calendar_dates[0][0]
        assert actual_first_monday == expected_first_monday
        assert table.get_cell_at(Coordinate(0, 0)).plain == "28"


async def test_next_month_when_month_is_december():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        month_calendar.month = 12
        month_calendar.next_month()
        table = month_calendar.query_one(DataTable)
        expected_first_monday = datetime.date(2021, 12, 27)
        actual_first_monday = month_calendar.calendar_dates[0][0]
        assert actual_first_monday == expected_first_monday
        assert table.get_cell_at(Coordinate(0, 0)).plain == "27"


async def test_move_cursor():
    app = MonthCalendarApp()
    async with app.run_test() as pilot:
        month_calendar = pilot.app.query_one(MonthCalendar)
        destination_date = datetime.date(2021, 6, 3)
        month_calendar.move_cursor(destination_date)
        table = month_calendar.query_one(DataTable)
        expected_coordinate = month_calendar.get_date_coordinate(destination_date)
        actual_coordinate = table.cursor_coordinate
        assert actual_coordinate == expected_coordinate
