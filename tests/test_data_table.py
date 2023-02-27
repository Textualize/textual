from __future__ import annotations

import pytest
from rich.style import Style
from rich.text import Text

from textual._wait import wait_for_idle
from textual.actions import SkipAction
from textual.app import App
from textual.coordinate import Coordinate
from textual.events import Click, MouseMove
from textual.message import Message
from textual.message_pump import MessagePump
from textual.widgets import DataTable
from textual.widgets.data_table import (
    CellDoesNotExist,
    CellKey,
    ColumnDoesNotExist,
    ColumnKey,
    DuplicateKey,
    Row,
    RowDoesNotExist,
    RowKey,
)

ROWS = [["0/0", "0/1"], ["1/0", "1/1"], ["2/0", "2/1"]]


class DataTableApp(App):
    messages_to_record = {
        "CellHighlighted",
        "CellSelected",
        "RowHighlighted",
        "RowSelected",
        "ColumnHighlighted",
        "ColumnSelected",
        "HeaderSelected",
        "RowLabelSelected",
    }

    def __init__(self):
        super().__init__()
        self.messages = []

    def compose(self):
        table = DataTable()
        table.focus()
        yield table

    def record_data_table_event(self, message: Message) -> None:
        name = message.__class__.__name__
        if name in self.messages_to_record:
            self.messages.append(message)

    @property
    def message_names(self) -> list[str]:
        return [message.__class__.__name__ for message in self.messages]

    async def _on_message(self, message: Message) -> None:
        await super()._on_message(message)
        self.record_data_table_event(message)


async def test_datatable_message_emission():
    app = DataTableApp()
    expected_messages = []
    async with app.run_test() as pilot:
        table = app.query_one(DataTable)

        assert app.message_names == expected_messages

        table.add_columns("Column0", "Column1")
        table.add_rows(ROWS)

        # A CellHighlighted is emitted because there were no rows (and
        # therefore no highlighted cells), but then a row was added, and
        # so the cell at (0, 0) became highlighted.
        expected_messages.append("CellHighlighted")
        await pilot.pause()
        assert app.message_names == expected_messages

        # Pressing Enter when the cursor is on a cell emits a CellSelected
        await pilot.press("enter")
        await pilot.pause()
        expected_messages.append("CellSelected")
        assert app.message_names == expected_messages

        # Moving the cursor left and up when the cursor is at origin
        # emits no events, since the cursor doesn't move at all.
        await pilot.press("left", "up")
        assert app.message_names == expected_messages

        # ROW CURSOR
        # Switch over to the row cursor... should emit a `RowHighlighted`
        table.cursor_type = "row"
        expected_messages.append("RowHighlighted")
        await pilot.pause()
        assert app.message_names == expected_messages

        # Select the row...
        await pilot.press("enter")
        await pilot.pause()
        expected_messages.append("RowSelected")
        assert app.message_names == expected_messages

        # COLUMN CURSOR
        # Switching to the column cursor emits a `ColumnHighlighted`
        table.cursor_type = "column"
        expected_messages.append("ColumnHighlighted")
        await pilot.pause()
        assert app.message_names == expected_messages

        # Select the column...
        await pilot.press("enter")
        expected_messages.append("ColumnSelected")
        await pilot.pause()
        assert app.message_names == expected_messages

        # NONE CURSOR
        # No messages get emitted at all...
        table.cursor_type = "none"
        await pilot.press("up", "down", "left", "right", "enter")
        await pilot.pause()
        # No new messages since cursor not visible
        assert app.message_names == expected_messages

        # Edge case - if show_cursor is False, and the cursor type
        # is changed back to a visible type, then no messages should
        # be emitted since the cursor is still not visible.
        table.show_cursor = False
        table.cursor_type = "cell"
        await pilot.press("up", "down", "left", "right", "enter")
        await pilot.pause()
        # No new messages since show_cursor = False
        assert app.message_names == expected_messages

        # Now when show_cursor is set back to True, the appropriate
        # message should be emitted for highlighting the cell.
        table.show_cursor = True
        expected_messages.append("CellHighlighted")
        await pilot.pause()
        assert app.message_names == expected_messages

        # Similarly for showing the cursor again when row or column
        # cursor was active before the cursor was hidden.
        table.show_cursor = False
        table.cursor_type = "row"
        table.show_cursor = True
        expected_messages.append("RowHighlighted")
        await pilot.pause()
        assert app.message_names == expected_messages

        table.show_cursor = False
        table.cursor_type = "column"
        table.show_cursor = True
        expected_messages.append("ColumnHighlighted")
        await pilot.pause()
        assert app.message_names == expected_messages

        # Likewise, if the cursor_type is "none", and we change the
        # show_cursor to True, then no events should be raised since
        # the cursor is still not visible to the user.
        table.cursor_type = "none"
        await pilot.press("up", "down", "left", "right", "enter")
        await pilot.pause()
        assert app.message_names == expected_messages


async def test_add_rows():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_columns("A", "B")
        row_keys = table.add_rows(ROWS)
        # We're given a key for each row
        assert len(row_keys) == len(ROWS)
        assert len(row_keys) == len(table._data)
        assert table.row_count == len(ROWS)
        # Each key can be used to fetch a row from the DataTable
        assert all(key in table._data for key in row_keys)


async def test_add_rows_user_defined_keys():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        key_a, key_b = table.add_columns("A", "B")
        algernon_key = table.add_row(*ROWS[0], key="algernon")
        table.add_row(*ROWS[1], key="charlie")
        auto_key = table.add_row(*ROWS[2])

        assert algernon_key == "algernon"
        # We get a RowKey object back, but we can use our own string *or* this object
        # to find the row we're looking for, they're considered equivalent for lookups.
        assert isinstance(algernon_key, RowKey)

        # Ensure the data in the table is mapped as expected
        first_row = {key_a: ROWS[0][0], key_b: ROWS[0][1]}
        assert table._data[algernon_key] == first_row
        assert table._data["algernon"] == first_row

        second_row = {key_a: ROWS[1][0], key_b: ROWS[1][1]}
        assert table._data["charlie"] == second_row

        third_row = {key_a: ROWS[2][0], key_b: ROWS[2][1]}
        assert table._data[auto_key] == third_row

        first_row = Row(algernon_key, height=1)
        assert table.rows[algernon_key] == first_row
        assert table.rows["algernon"] == first_row


async def test_add_row_duplicate_key():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_column("A")
        table.add_row("1", key="1")
        with pytest.raises(DuplicateKey):
            table.add_row("2", key="1")  # Duplicate row key


async def test_add_column_duplicate_key():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_column("A", key="A")
        with pytest.raises(DuplicateKey):
            table.add_column("B", key="A")  # Duplicate column key


async def test_add_column_with_width():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        column = table.add_column("ABC", width=10, key="ABC")
        row = table.add_row("123")
        assert table.get_cell(row, column) == "123"
        assert table.columns[column].width == 10
        assert table.columns[column].render_width == 12  # 10 + (2 padding)


async def test_add_columns():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        column_keys = table.add_columns("1", "2", "3")
        assert len(column_keys) == 3
        assert len(table.columns) == 3


async def test_add_columns_user_defined_keys():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        key = table.add_column("Column", key="donut")
        assert key == "donut"
        assert key == key


async def test_clear():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        assert table.cursor_coordinate == Coordinate(0, 0)
        assert table.hover_coordinate == Coordinate(0, 0)

        # Add some data and update cursor positions
        table.add_column("Column0")
        table.add_rows([["Row0"], ["Row1"], ["Row2"]])
        table.cursor_coordinate = Coordinate(1, 0)
        table.hover_coordinate = Coordinate(2, 0)

        # Ensure the cursor positions are reset to origin on clear()
        table.clear()
        assert table.cursor_coordinate == Coordinate(0, 0)
        assert table.hover_coordinate == Coordinate(0, 0)

        # Ensure that the table has been cleared
        assert table._data == {}
        assert table.rows == {}
        assert table.row_count == 0
        assert len(table._row_locations) == 0
        assert len(table._column_locations) == 1
        assert len(table.columns) == 1

        # Clearing the columns too
        table.clear(columns=True)
        assert len(table._column_locations) == 0
        assert len(table.columns) == 0


async def test_column_labels() -> None:
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_columns("1", "2", "3")
        actual_labels = [col.label.plain for col in table.columns.values()]
        expected_labels = ["1", "2", "3"]
        assert actual_labels == expected_labels


async def test_initial_column_widths() -> None:
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        foo, bar = table.add_columns("foo", "bar")

        assert table.columns[foo].width == 3
        assert table.columns[bar].width == 3
        table.add_row("Hello", "World!")
        await wait_for_idle()
        assert table.columns[foo].content_width == 5
        assert table.columns[bar].content_width == 6

        table.add_row("Hello World!!!", "fo")
        await wait_for_idle()
        assert table.columns[foo].content_width == 14
        assert table.columns[bar].content_width == 6


async def test_get_cell_returns_value_at_cell():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_column("Column1", key="C1")
        table.add_row("TargetValue", key="R1")
        assert table.get_cell("R1", "C1") == "TargetValue"


async def test_get_cell_invalid_row_key():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_column("Column1", key="C1")
        table.add_row("TargetValue", key="R1")
        with pytest.raises(CellDoesNotExist):
            table.get_cell("INVALID_ROW", "C1")


async def test_get_cell_invalid_column_key():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_column("Column1", key="C1")
        table.add_row("TargetValue", key="R1")
        with pytest.raises(CellDoesNotExist):
            table.get_cell("R1", "INVALID_COLUMN")


async def test_get_cell_at_returns_value_at_cell():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_columns("A", "B")
        table.add_rows(ROWS)
        assert table.get_cell_at(Coordinate(0, 0)) == "0/0"


async def test_get_cell_at_exception():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_columns("A", "B")
        table.add_rows(ROWS)
        with pytest.raises(CellDoesNotExist):
            table.get_cell_at(Coordinate(9999, 0))


async def test_get_row():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        a, b, c = table.add_columns("A", "B", "C")
        first_row = table.add_row(2, 4, 1)
        second_row = table.add_row(3, 2, 1)
        assert table.get_row(first_row) == [2, 4, 1]
        assert table.get_row(second_row) == [3, 2, 1]

        # Even if row positions change, keys should always refer to same rows.
        table.sort(b)
        assert table.get_row(first_row) == [2, 4, 1]
        assert table.get_row(second_row) == [3, 2, 1]


async def test_get_row_invalid_row_key():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        with pytest.raises(RowDoesNotExist):
            table.get_row("INVALID")


async def test_get_row_at():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        a, b, c = table.add_columns("A", "B", "C")
        table.add_row(2, 4, 1)
        table.add_row(3, 2, 1)
        assert table.get_row_at(0) == [2, 4, 1]
        assert table.get_row_at(1) == [3, 2, 1]

        # If we sort, then the rows present at the indices *do* change!
        table.sort(b)

        # Since we sorted on column "B", the rows at indices 0 and 1 are swapped.
        assert table.get_row_at(0) == [3, 2, 1]
        assert table.get_row_at(1) == [2, 4, 1]


@pytest.mark.parametrize("index", (-1, 2))
async def test_get_row_at_invalid_index(index):
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_columns("A", "B", "C")
        table.add_row(2, 4, 1)
        table.add_row(3, 2, 1)
        with pytest.raises(RowDoesNotExist):
            table.get_row_at(index)


async def test_get_column():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        a, b = table.add_columns("A", "B")
        table.add_rows(ROWS)
        cells = table.get_column(a)
        assert next(cells) == ROWS[0][0]
        assert next(cells) == ROWS[1][0]
        assert next(cells) == ROWS[2][0]
        with pytest.raises(StopIteration):
            next(cells)


async def test_get_column_invalid_key():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        with pytest.raises(ColumnDoesNotExist):
            list(table.get_column("INVALID"))


async def test_get_column_at():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_columns("A", "B")
        table.add_rows(ROWS)

        first_column = list(table.get_column_at(0))
        assert first_column == [ROWS[0][0], ROWS[1][0], ROWS[2][0]]

        second_column = list(table.get_column_at(1))
        assert second_column == [ROWS[0][1], ROWS[1][1], ROWS[2][1]]


@pytest.mark.parametrize("index", [-1, 5])
async def test_get_column_at_invalid_index(index):
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        with pytest.raises(ColumnDoesNotExist):
            list(table.get_column_at(index))


async def test_update_cell_cell_exists():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_column("A", key="A")
        table.add_row("1", key="1")
        table.update_cell("1", "A", "NEW_VALUE")
        assert table.get_cell("1", "A") == "NEW_VALUE"


async def test_update_cell_cell_doesnt_exist():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_column("A", key="A")
        table.add_row("1", key="1")
        with pytest.raises(CellDoesNotExist):
            table.update_cell("INVALID", "CELL", "Value")


async def test_update_cell_at_coordinate_exists():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        column_0, column_1 = table.add_columns("A", "B")
        row_0, *_ = table.add_rows(ROWS)

        table.update_cell_at(Coordinate(0, 1), "newvalue")
        assert table.get_cell(row_0, column_1) == "newvalue"


async def test_update_cell_at_coordinate_doesnt_exist():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_columns("A", "B")
        table.add_rows(ROWS)
        with pytest.raises(CellDoesNotExist):
            table.update_cell_at(Coordinate(999, 999), "newvalue")


@pytest.mark.parametrize(
    "label,new_value,new_content_width",
    [
        # Shorter than initial cell value, larger than label => width remains same
        ("A", "BB", 3),
        # Larger than cell value, shorter than label => width remains that of label
        ("1234567", "1234", 7),
        # Shorter than cell value, shorter than label => width remains same
        ("12345", "123", 5),
        # Larger than cell value, larger than label => width updates to new cell value
        ("12345", "123456789", 9),
    ],
)
async def test_update_cell_at_column_width(label, new_value, new_content_width):
    # Initial cell values are length 3. Let's update cell content and ensure
    # that the width of the column is correct given the new cell content widths
    # and the label of the column the cell is in.
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        key, _ = table.add_columns(label, "Column2")
        table.add_rows(ROWS)
        first_column = table.columns.get(key)

        table.update_cell_at(Coordinate(0, 0), new_value, update_width=True)
        await wait_for_idle()
        assert first_column.content_width == new_content_width
        assert first_column.render_width == new_content_width + 2


async def test_coordinate_to_cell_key():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        column_key, _ = table.add_columns("Column0", "Column1")
        row_key = table.add_row("A", "B")

        cell_key = table.coordinate_to_cell_key(Coordinate(0, 0))
        assert cell_key == CellKey(row_key, column_key)


async def test_coordinate_to_cell_key_invalid_coordinate():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        with pytest.raises(CellDoesNotExist):
            table.coordinate_to_cell_key(Coordinate(9999, 9999))


def make_click_event(sender: MessagePump):
    return Click(
        sender=sender,
        x=1,
        y=2,
        delta_x=0,
        delta_y=0,
        button=0,
        shift=False,
        meta=False,
        ctrl=False,
    )


async def test_datatable_on_click_cell_cursor():
    """When the cell cursor is used, and we click, we emit a CellHighlighted
    *and* a CellSelected message for the cell that was clicked.
    Regression test for https://github.com/Textualize/textual/issues/1723"""
    app = DataTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(DataTable)
        click = make_click_event(app)
        column_key = table.add_column("ABC")
        table.add_row("123")
        row_key = table.add_row("456")
        table.on_click(event=click)
        await pilot.pause()
        # There's two CellHighlighted events since a cell is highlighted on initial load,
        # then when we click, another cell is highlighted (and selected).
        assert app.message_names == [
            "CellHighlighted",
            "CellHighlighted",
            "CellSelected",
        ]
        cell_highlighted_event: DataTable.CellHighlighted = app.messages[1]
        assert cell_highlighted_event.sender is table
        assert cell_highlighted_event.value == "456"
        assert cell_highlighted_event.cell_key == CellKey(row_key, column_key)
        assert cell_highlighted_event.coordinate == Coordinate(1, 0)

        cell_selected_event: DataTable.CellSelected = app.messages[2]
        assert cell_selected_event.sender is table
        assert cell_selected_event.value == "456"
        assert cell_selected_event.cell_key == CellKey(row_key, column_key)
        assert cell_selected_event.coordinate == Coordinate(1, 0)


async def test_on_click_row_cursor():
    """When the row cursor is used, and we click, we emit a RowHighlighted
    *and* a RowSelected message for the row that was clicked."""
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.cursor_type = "row"
        click = make_click_event(app)
        table.add_column("ABC")
        table.add_row("123")
        row_key = table.add_row("456")
        table.on_click(event=click)
        await wait_for_idle(0)
        assert app.message_names == ["RowHighlighted", "RowHighlighted", "RowSelected"]

        row_highlighted: DataTable.RowHighlighted = app.messages[1]
        assert row_highlighted.sender is table
        assert row_highlighted.row_key == row_key
        assert row_highlighted.cursor_row == 1

        row_selected: DataTable.RowSelected = app.messages[2]
        assert row_selected.sender is table
        assert row_selected.row_key == row_key
        assert row_highlighted.cursor_row == 1


async def test_on_click_column_cursor():
    """When the column cursor is used, and we click, we emit a ColumnHighlighted
    *and* a ColumnSelected message for the column that was clicked."""
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.cursor_type = "column"
        column_key = table.add_column("ABC")
        table.add_row("123")
        table.add_row("456")
        click = make_click_event(app)
        table.on_click(event=click)
        await wait_for_idle(0)
        assert app.message_names == [
            "ColumnHighlighted",
            "ColumnHighlighted",
            "ColumnSelected",
        ]
        column_highlighted: DataTable.ColumnHighlighted = app.messages[1]
        assert column_highlighted.sender is table
        assert column_highlighted.column_key == column_key
        assert column_highlighted.cursor_column == 0

        column_selected: DataTable.ColumnSelected = app.messages[2]
        assert column_selected.sender is table
        assert column_selected.column_key == column_key
        assert column_highlighted.cursor_column == 0


async def test_hover_coordinate():
    """Ensure that the hover_coordinate reactive is updated as expected."""
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_column("ABC")
        table.add_row("123")
        table.add_row("456")
        assert table.hover_coordinate == Coordinate(0, 0)

        mouse_move = MouseMove(
            sender=app,
            x=1,
            y=2,
            delta_x=0,
            delta_y=0,
            button=0,
            shift=False,
            meta=False,
            ctrl=False,
            style=Style(meta={"row": 1, "column": 2}),
        )
        table.on_mouse_move(mouse_move)
        await wait_for_idle(0)
        assert table.hover_coordinate == Coordinate(1, 2)


async def test_header_selected():
    """Ensure that a HeaderSelected event gets posted when we click
    on the header in the DataTable."""
    app = DataTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(DataTable)
        column_key = table.add_column("number")
        table.add_row(3)
        click_event = Click(
            sender=table,
            x=3,
            y=0,
            delta_x=0,
            delta_y=0,
            button=1,
            shift=False,
            meta=False,
            ctrl=False,
        )
        await pilot.pause()
        table.on_click(click_event)
        await pilot.pause()
        message: DataTable.HeaderSelected = app.messages[-1]
        assert message.sender is table
        assert message.label == Text("number")
        assert message.column_index == 0
        assert message.column_key == column_key

        # Now hide the header and click in the exact same place - no additional message emitted.
        table.show_header = False
        table.on_click(click_event)
        await pilot.pause()
        assert app.message_names.count("HeaderSelected") == 1


async def test_row_label_selected():
    """Ensure that the DataTable sends a RowLabelSelected event when
    the user clicks on a row label."""
    app = DataTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(DataTable)
        table.add_column("number")
        row_key = table.add_row(3, label="A")
        click_event = Click(
            sender=table,
            x=1,
            y=1,
            delta_x=0,
            delta_y=0,
            button=1,
            shift=False,
            meta=False,
            ctrl=False,
        )
        await pilot.pause()
        table.on_click(click_event)
        await pilot.pause()
        message: DataTable.RowLabelSelected = app.messages[-1]
        assert message.sender is table
        assert message.label == Text("A")
        assert message.row_index == 0
        assert message.row_key == row_key

        # Now hide the row label and click in the same place - no additional message emitted.
        table.show_row_labels = False
        table.on_click(click_event)
        await pilot.pause()
        assert app.message_names.count("RowLabelSelected") == 1


async def test_sort_coordinate_and_key_access():
    """Ensure that, after sorting, that coordinates and cell keys
    can still be used to retrieve the correct cell."""
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        column = table.add_column("number")
        row_three = table.add_row(3)
        row_one = table.add_row(1)
        row_two = table.add_row(2)

        # Items inserted in correct initial positions (before sort)
        assert table.get_cell_at(Coordinate(0, 0)) == 3
        assert table.get_cell_at(Coordinate(1, 0)) == 1
        assert table.get_cell_at(Coordinate(2, 0)) == 2

        table.sort(column)

        # The keys still refer to the same cells...
        assert table.get_cell(row_one, column) == 1
        assert table.get_cell(row_two, column) == 2
        assert table.get_cell(row_three, column) == 3

        # ...even though the values under the coordinates have changed...
        assert table.get_cell_at(Coordinate(0, 0)) == 1
        assert table.get_cell_at(Coordinate(1, 0)) == 2
        assert table.get_cell_at(Coordinate(2, 0)) == 3

        assert table.ordered_rows[0].key == row_one
        assert table.ordered_rows[1].key == row_two
        assert table.ordered_rows[2].key == row_three


async def test_sort_reverse_coordinate_and_key_access():
    """Ensure that, after sorting, that coordinates and cell keys
    can still be used to retrieve the correct cell."""
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        column = table.add_column("number")
        row_three = table.add_row(3)
        row_one = table.add_row(1)
        row_two = table.add_row(2)

        # Items inserted in correct initial positions (before sort)
        assert table.get_cell_at(Coordinate(0, 0)) == 3
        assert table.get_cell_at(Coordinate(1, 0)) == 1
        assert table.get_cell_at(Coordinate(2, 0)) == 2

        table.sort(column, reverse=True)

        # The keys still refer to the same cells...
        assert table.get_cell(row_one, column) == 1
        assert table.get_cell(row_two, column) == 2
        assert table.get_cell(row_three, column) == 3

        # ...even though the values under the coordinates have changed...
        assert table.get_cell_at(Coordinate(0, 0)) == 3
        assert table.get_cell_at(Coordinate(1, 0)) == 2
        assert table.get_cell_at(Coordinate(2, 0)) == 1

        assert table.ordered_rows[0].key == row_three
        assert table.ordered_rows[1].key == row_two
        assert table.ordered_rows[2].key == row_one


async def test_cell_cursor_highlight_events():
    app = DataTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(DataTable)
        column_one_key, column_two_key = table.add_columns("A", "B")
        _ = table.add_row(0, 1)
        row_two_key = table.add_row(2, 3)

        # Since initial position is (0, 0), cursor doesn't move so no event posted
        table.action_cursor_up()
        table.action_cursor_left()

        await pilot.pause()
        assert table.app.message_names == [
            "CellHighlighted"
        ]  # Initial highlight on load

        # Move the cursor one cell down, and check the highlighted event posted
        table.action_cursor_down()
        await pilot.pause()
        assert len(table.app.messages) == 2
        latest_message: DataTable.CellHighlighted = table.app.messages[-1]
        assert isinstance(latest_message, DataTable.CellHighlighted)
        assert latest_message.value == 2
        assert latest_message.coordinate == Coordinate(1, 0)
        assert latest_message.cell_key == CellKey(row_two_key, column_one_key)

        # Now move the cursor to the right, and check highlighted event posted
        table.action_cursor_right()
        await pilot.pause()
        assert len(table.app.messages) == 3
        latest_message = table.app.messages[-1]
        assert latest_message.coordinate == Coordinate(1, 1)
        assert latest_message.cell_key == CellKey(row_two_key, column_two_key)


async def test_row_cursor_highlight_events():
    app = DataTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("A", "B")
        row_one_key = table.add_row(0, 1)
        row_two_key = table.add_row(2, 3)

        # Since initial position is row_index=0, the following actions do nothing.
        with pytest.raises(SkipAction):
            table.action_cursor_up()
            table.action_cursor_left()
            table.action_cursor_right()

        await pilot.pause()
        assert table.app.message_names == ["RowHighlighted"]  # Initial highlight

        # Move the row cursor from row 0 to row 1, check the highlighted event posted
        table.action_cursor_down()
        await pilot.pause()
        assert len(table.app.messages) == 2
        latest_message: DataTable.RowHighlighted = table.app.messages[-1]
        assert isinstance(latest_message, DataTable.RowHighlighted)
        assert latest_message.row_key == row_two_key
        assert latest_message.cursor_row == 1

        # Move the row cursor back up to row 0, check the highlighted event posted
        table.action_cursor_up()
        await pilot.pause()
        assert len(table.app.messages) == 3
        latest_message = table.app.messages[-1]
        assert latest_message.row_key == row_one_key
        assert latest_message.cursor_row == 0


async def test_column_cursor_highlight_events():
    app = DataTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(DataTable)
        table.cursor_type = "column"
        column_one_key, column_two_key = table.add_columns("A", "B")
        table.add_row(0, 1)
        table.add_row(2, 3)

        # Since initial position is column_index=0, the following actions do nothing.
        with pytest.raises(SkipAction):
            table.action_cursor_left()
            table.action_cursor_up()
            table.action_cursor_down()

        await pilot.pause()
        assert table.app.message_names == ["ColumnHighlighted"]  # Initial highlight

        # Move the column cursor from column 0 to column 1,
        # check the highlighted event posted
        table.action_cursor_right()
        await pilot.pause()
        assert len(table.app.messages) == 2
        latest_message: DataTable.ColumnHighlighted = table.app.messages[-1]
        assert isinstance(latest_message, DataTable.ColumnHighlighted)
        assert latest_message.column_key == column_two_key
        assert latest_message.cursor_column == 1

        # Move the column cursor left, back to column 0,
        # check the highlighted event posted again.
        table.action_cursor_left()
        await pilot.pause()
        assert len(table.app.messages) == 3
        latest_message = table.app.messages[-1]
        assert latest_message.column_key == column_one_key
        assert latest_message.cursor_column == 0


async def test_reuse_row_key_after_clear():
    """Regression test for https://github.com/Textualize/textual/issues/1806"""
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_columns("A", "B")
        table.add_row(0, 1, key="ROW1")
        table.add_row(2, 3, key="ROW2")
        table.clear()
        table.add_row(4, 5, key="ROW1")  # Reusing the same keys as above
        table.add_row(7, 8, key="ROW2")
        assert table.get_row("ROW1") == [4, 5]
        assert table.get_row("ROW2") == [7, 8]


async def test_reuse_column_key_after_clear():
    """Regression test for https://github.com/Textualize/textual/issues/1806"""
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_column("A", key="COLUMN1")
        table.add_column("B", key="COLUMN2")
        table.clear(columns=True)
        table.add_column("C", key="COLUMN1")  # Reusing the same keys as above
        table.add_column("D", key="COLUMN2")
        table.add_row(1, 2)
        assert list(table.get_column("COLUMN1")) == [1]
        assert list(table.get_column("COLUMN2")) == [2]


def test_key_equals_equivalent_string():
    text = "Hello"
    key = RowKey(text)
    assert key == text
    assert hash(key) == hash(text)


def test_key_doesnt_match_non_equal_string():
    key = ColumnKey("123")
    text = "laksjdlaskjd"
    assert key != text
    assert hash(key) != hash(text)


def test_key_equals_self():
    row_key = RowKey()
    column_key = ColumnKey()
    assert row_key == row_key
    assert column_key == column_key
    assert row_key != column_key


def test_key_string_lookup():
    # Indirectly covered by other tests, but let's explicitly document
    # in tests how we intend for the keys to work for cache lookups.
    dictionary = {
        "foo": "bar",
        RowKey("hello"): "world",
    }
    assert dictionary["foo"] == "bar"
    assert dictionary[RowKey("foo")] == "bar"
    assert dictionary["hello"] == "world"
    assert dictionary[RowKey("hello")] == "world"
